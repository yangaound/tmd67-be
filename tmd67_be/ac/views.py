import datetime
import hashlib
import subprocess
import time
import urllib.parse

import jwt
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from requests_oauthlib import OAuth2Session
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.response import Response

from .models import Order, PaymentRecord, Ticket, TicketProduct
from .serializers import (
    CreateIdentitySerializer,
    OrderSerializer,
    PaymentRecordSerializer,
    RetrieveIdentitySerializer,
    TicketProductSerializer,
    TicketSerializer,
)


class ACIDRegister(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = CreateIdentitySerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        if User.objects.filter(email=validated_data["email"]).exists():
            raise exceptions.ValidationError(
                {
                    "email": [
                        "This email was registered; please use forgot password to reset it."
                    ]
                }
            )
        user = User(**validated_data)
        user.username = validated_data["email"]
        user.set_password(validated_data["password"])
        user.save()
        serializer = self.get_serializer(user)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ACIDDirectory(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = RetrieveIdentitySerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        return Response(
            self.serializer_class(
                request.user, context=self.get_serializer_context()
            ).data
        )


class TicketProductViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("chinese_name", "english_name")
    queryset = TicketProduct.objects.all()
    serializer_class = TicketProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    filterset_fields = ("state",)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    filterset_fields = (
        "first_name",
        "last_name",
        "order",
        "ticket_product",
        "club",
    )
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)


class PaymentRecordViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    filterset_fields = ("order", "merchant_id", "is_paid")
    permission_classes = (permissions.IsAuthenticated,)
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a payment-record to store translation information
        Return a webpage, from which connect to NewebPay's payment gateway.
        """
        data = self.request.data

        # verify order
        if not (
            data["order"].isdigit()
            and Order.objects.filter(id=data["order"]).exists()
        ):
            raise exceptions.ValidationError("Order not found.")

        # translation info
        order = Order.objects.get(id=data["order"])
        conf = settings.NEWEB_PAY
        time_stamp = int(time.time())
        translation_data = {
            "MerchantID": conf["MerchantID"],
            "TimeStamp": time_stamp,
            "Version": "2.0",
            "RespondType": "application/json",
            "MerchantOrderNo": f"{conf['MerchantID']}__{order.id}",
            "Amt": order.amount,
            "NotifyURL": conf["NotifyURL"],
            "ReturnURL": "",
            "ItemDesc": "TMD67",
        }
        payment_record = PaymentRecord(
            order=order,
            due_date=datetime.datetime.today() + datetime.timedelta(days=3),
            description=data["description"] or None,
            merchant_id=conf["MerchantID"],
            is_paid=False,
        )
        payment_record.save()

        # encrypt translation info with php
        urlencode_translation_data = urllib.parse.urlencode(translation_data)
        _cmd = f"""php tmd67_be/newebpay_encrypt/encrypt.php
            '{urlencode_translation_data}'
            '{conf['HashKey']}'
            '{conf['HashIV']}'
        """
        _process = subprocess.Popen(_cmd.split(), stdout=subprocess.PIPE)
        _stdout, ret_code = _process.communicate()
        encrypted_data = _stdout.decode("utf8")
        if ret_code != 0:
            raise exceptions.ValidationError(
                f"execute '{_cmd}' fail: {encrypted_data}"
            )

        # prepare context for rendering page
        _check_code = f"HashKey={conf['HashKey']}&{encrypted_data}&HashIV={conf['HashIV']}"
        hash_code = (
            hashlib.sha256(_check_code.encode("utf8")).hexdigest().upper()
        )
        context = {
            "mpg_gateway": conf["mpg_gateway"],
            "HashKey": conf["HashKey"],
            "MerchantID": conf["MerchantID"],
            "TradeInfo": encrypted_data,
            "TradeSha": hash_code,
        }
        webpage = render(request, "newebpay.html", context)

        return webpage


def google_auth_rdr(req):
    conf = settings.OAUTH2["Google"]
    oauth = OAuth2Session(
        conf["client_id"],
        redirect_uri=conf["redirect_uri"],
        scope=conf["scope"],
        state=req.GET.get("next", "/user-directory/"),
    )
    authorization_url, state = oauth.authorization_url(
        conf["auth_uri"],
        req.GET.get("next", ""),
        access_type="offline",
        prompt="consent",
    )
    return render(req, "auth_uri.html", {"AUTH_URI": authorization_url})


def google_auth_cb(req):
    data, status_code = {"error": req.GET.get("error", None)}, 400
    if req.GET.get("code"):
        conf = settings.OAUTH2["Google"]
        try:
            oauth = OAuth2Session(
                conf["client_id"], redirect_uri=conf["redirect_uri"]
            )
            data = oauth.fetch_token(
                conf["token_uri"],
                code=req.GET.get("code"),
                client_secret=conf["client_secret"],
            )
            id_token = data["id_token"]
            state = req.GET.get("state")
            open_info = jwt.decode(
                id_token, options={"verify_signature": False}
            )
            try:
                user = User.objects.get(username=open_info["email"])
            except User.DoesNotExist:
                user = User(
                    username=open_info["email"],
                    first_name=open_info["given_name"],
                    last_name=open_info["family_name"],
                )
                user.save()
            login(
                req, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return HttpResponseRedirect(state)
        except Exception as e:
            data.update(message=req.GET.get("error", "") + " " + str(e))
            return JsonResponse(data, status=500)
    return JsonResponse(data, status=status_code)
