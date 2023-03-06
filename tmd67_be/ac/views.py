import hashlib
import json
import logging
import urllib.parse

import jwt
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import QueryDict
from django.http.response import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.middleware.csrf import get_token
from django.shortcuts import render
from requests_oauthlib import OAuth2Session
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, PaymentRecord, Ticket, TicketProduct
from .neweb_pay_crypto import decrypt_trade_info, encrypt_trade_info
from .serializers import (
    CreateIdentitySerializer,
    IdentitySerializer,
    OrderSerializer,
    PaymentRecordSerializer,
    RetrieveIdentitySerializer,
    TicketProductSerializer,
    TicketSerializer,
)


class ACIDRegister(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = CreateIdentitySerializer
    queryset = User.objects.all()

    @transaction.atomic
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


def csrf_token(request):
    csrftoken = get_token(request)
    res = JsonResponse({settings.CSRF_COOKIE_NAME: csrftoken})
    res.set_cookie(settings.CSRF_COOKIE_NAME, csrftoken)
    return res


@transaction.atomic
def user_login(request):
    try:
        if request.content_type == "application/json":
            serializer = IdentitySerializer(data=json.load(request))
        else:
            serializer = IdentitySerializer(
                data=QueryDict(request.POST.urlencode())
            )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
    except Exception as e:
        logging.warning(str(e))
        raise PermissionDenied

    qs = User.objects.filter(username=validated_data["email"])
    if not qs.exists():
        logging.warning(
            "The email '{email}' does not exist.".format(**validated_data)
        )
        raise PermissionDenied

    user = qs.first()
    if not user.check_password(validated_data["password"]):
        logging.warning(
            "Incorrect password entered for user '{email}'.".format(
                **validated_data
            )
        )
        raise PermissionDenied

    login(
        request,
        user,
        backend="django.contrib.auth.backends.ModelBackend",
    )
    return HttpResponse()


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
        "ticket_products",
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
    filterset_fields = ("order", "merchant_id", "status")
    permission_classes = (permissions.IsAuthenticated,)
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer

    @staticmethod
    def _write_off_trade(request):
        data = request.data
        conf = settings.NEWEB_PAY

        # Decrypt transaction info
        _transaction_msg = decrypt_trade_info(
            data["TradeInfo"],
            conf["HashKey"],
            conf["HashIV"],
        )
        transaction_data = json.loads(_transaction_msg)

        # Retrieve the Payment Record corresponding to the transaction
        # NeWebPay’s parameter `MerchantOrderNo` consists of f"{merchant_id}_{payment_record_id}_{timestamp}"
        try:
            merchant_id, payment_record_id, _ = transaction_data["Result"][
                "MerchantOrderNo"
            ].split("_")
            payment_record = PaymentRecord.objects.get(
                id=payment_record_id,
                merchant_id=data.get("MerchantID"),
                version=data.get("Version"),
            )
        except PaymentRecord.DoesNotExist:
            raise exceptions.PermissionDenied

        if payment_record.order.state == "paid":
            return

        # Save the transaction result
        payment_record.status = transaction_data["Status"]
        payment_record.message = transaction_data["Message"]
        payment_record.result = json.dumps(transaction_data["Result"])
        # Write off
        # transit the order.state to 'paid' only if status is 'SUCCESS'
        if payment_record.status == "SUCCESS":
            payment_record.order.state = "paid"
        payment_record.save()
        payment_record.order.save()

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    @staticmethod
    @api_view(["POST"])
    @transaction.atomic
    def neweb_pay_notify(request):
        """Handle NewebPay's NotifyURL for completing the payment process"""
        PaymentRecordViewSet._write_off_trade(request)
        return Response(None, 200)

    @staticmethod
    @api_view(["POST"])
    @transaction.atomic
    def neweb_pay_return(request):
        """Handle NewebPay's ReturnURL for completing the payment process.
        Redirect to home-page of the user'
        """
        PaymentRecordViewSet._write_off_trade(request)
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL + "/me")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Creates a payment record to document the NewebPay trade and updates the `order.state` to 'unpaid'.
        Then, it responds with either HTML or JSON
        """
        conf = settings.NEWEB_PAY

        # Extract input
        order_id = self.request.data.get("order")
        description = self.request.data.get("description", "")

        # Validate the input order
        # check if the order exists, its state is not equal to 'paid',
        # and it belongs to the currently authenticated user.
        if not str(order_id).isdigit():
            raise exceptions.ValidationError(
                {"order": ["Order format unexpected."]}
            )

        order_qs = Order.objects.filter(id=order_id)
        if request.user.is_authenticated:
            order_qs = order_qs.filter(user=request.user)

        if not order_qs.exists():
            raise exceptions.ValidationError({"order": [f"Order not found."]})

        order = order_qs[0]
        if order.state == "paid":
            raise exceptions.ValidationError({"order": [f"Order had paid."]})

        # Prepare transaction info
        # reserve a `MerchantOrderNo`, which consists of the f"{merchant_id}_{payment_record_id}_{timestamp}" string
        # truncated to 30 characters.
        payment_record = PaymentRecord(
            order=order,
            merchant_id=conf["MerchantID"],
            respond_type="JSON",
            version=conf["Version"],
            description=description,
            status=None,
        )
        payment_record.save()
        reversed_ts = str(int(payment_record.created_time.timestamp()))[::-1]
        merchant_order_no = (
            f"{conf['MerchantID']}_{payment_record.id}_{reversed_ts}"[:30]
        )
        payment_record.merchant_order_no = merchant_order_no
        payment_record.save()

        transaction_data = {
            "MerchantID": conf["MerchantID"],
            "RespondType": "JSON",
            "TimeStamp": reversed_ts,
            "Version": conf["Version"],
            "MerchantOrderNo": merchant_order_no,
            "Amt": order.amount,
            "ItemDesc": conf["ItemDesc"],
            "NotifyURL": conf["NotifyURL"],
            "ReturnURL": conf["ReturnURL"],
            "Email": request.user.username,
        }

        # Encrypt payment info
        urlencode_translation_data = urllib.parse.urlencode(transaction_data)
        encrypted_data = encrypt_trade_info(
            urlencode_translation_data,
            conf["HashKey"],
            conf["HashIV"],
        )
        encrypted_data = encrypted_data.decode()

        # Prepare context dictionary
        _check_code = f"HashKey={conf['HashKey']}&{encrypted_data}&HashIV={conf['HashIV']}"
        hash_code = (
            hashlib.sha256(_check_code.encode("utf8")).hexdigest().upper()
        )
        context = {
            "MPG_GW": conf["MPG_GW"],
            "MerchantID": conf["MerchantID"],
            "TradeInfo": encrypted_data,
            "TradeSha": hash_code,
            "Amount": order.amount,
            "Version": conf["Version"],
        }

        # Transit order state to 'unpaid'
        # 'unpaid' means that the user has confirmed the purchased item,
        # and the backend has reserved the MerchantOrderNo and is waiting for the payment to be credited.
        order.state = "unpaid"
        order.save()

        # Render payment page/json with the context dictionary based on content-type
        # the format of the response depends on the frontend implementation.
        # if an HTML form with a submit button is used to call this API,
        # the response is typically an HTML page. however,
        # if a library is used to make the API call and the Content-Type header is set to application/json,
        # the response is JSON data.
        if request.content_type == "application/json":
            return Response(context, status=status.HTTP_201_CREATED)
        return render(request, "neweb_pay.html", context)


def google_auth_rdr(req):
    conf = settings.OAUTH2["Google"]
    oauth = OAuth2Session(
        conf["client_id"],
        redirect_uri=conf["redirect_uri"],
        scope=conf["scope"],
        state=req.GET.get("next", settings.LOGIN_REDIRECT_URL),
    )
    authorization_url, state = oauth.authorization_url(
        conf["auth_uri"],
        req.GET.get("next", ""),
        access_type="offline",
        prompt="consent",
    )
    return render(req, "auth_uri.html", {"AUTH_URI": authorization_url})


@transaction.atomic
def google_auth_cb(request):
    conf = settings.OAUTH2["Google"]

    if request.GET.get("code"):
        try:
            oauth = OAuth2Session(
                conf["client_id"], redirect_uri=conf["redirect_uri"]
            )
            idp_resp = oauth.fetch_token(
                conf["token_uri"],
                code=request.GET.get("code"),
                client_secret=conf["client_secret"],
            )
            id_token = idp_resp["id_token"]
            state = request.GET.get("state")
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
                    email=open_info["email"],
                )
                user.save()
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            resp = HttpResponseRedirect(state)
        except Exception as e:
            resp = JsonResponse({"error": str(e)}, status=500)
    else:
        resp = JsonResponse({"error": request.GET.get("error", None)}, 400)

    return resp
