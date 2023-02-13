import datetime
import hashlib
import json
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
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, PaymentRecord, Ticket, TicketProduct
from .neweb_pay_crypto import decrypt_trade_info, encrypt_trade_info
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
    def _write_off_trade(request, *args, **kwargs):
        data = request.data
        neweb_pay_conf = settings.NEWEB_PAY

        # Decrypt transaction info
        _transaction_msg = decrypt_trade_info(
            data["TradeInfo"],
            neweb_pay_conf["HashKey"],
            neweb_pay_conf["HashIV"],
        )
        transaction_data = json.loads(_transaction_msg)

        # Retrieve the Payment Record corresponding to the transaction
        merchant_id, payment_record_id = transaction_data["Result"][
            "MerchantOrderNo"
        ].split("_")
        try:
            payment_record = PaymentRecord.objects.get(
                id=payment_record_id, merchant_id=merchant_id
            )
        except PaymentRecord.DoesNotExist:
            raise exceptions.ValidationError("PaymentRecord not found.")

        # Save the transaction result
        payment_record.status = transaction_data["Status"]
        payment_record.message = transaction_data["Message"]
        payment_record.result = json.dumps(transaction_data["Result"])
        # write-off
        if payment_record.status == "SUCCESS":
            payment_record.order.state = "paid"
        payment_record.save()
        payment_record.order.save()

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    @staticmethod
    @api_view(["POST"])
    def neweb_pay_notify(request, *args, **kwargs):
        """Handle NewebPay's NotifyURL"""
        data = PaymentRecordViewSet._write_off_trade(request, *args, **kwargs)
        return Response(data)

    @staticmethod
    @api_view(["POST"])
    def neweb_pay_return(request, *args, **kwargs):
        """Handle NewebPay's ReturnURL"""
        _ = PaymentRecordViewSet._write_off_trade(request, *args, **kwargs)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    def create(self, request, *args, **kwargs):
        """
        Create a payment record to record NewebPay’s trade.
        Return a webpage, from which connect to NewebPay's payment gateway.
        """
        data = self.request.data

        # Verify the input `order`
        if not data["order"].isdigit():
            raise exceptions.ValidationError("Order format unexpected.")

        order_qs = Order.objects.filter(id=data["order"])
        if request.user.is_authenticated:
            data["order"].isdigit()
            order_qs = order_qs.filter(user=request.user)

        if not order_qs.exists():
            raise exceptions.ValidationError("Order not found.")

        # Prepare transaction info
        order = Order.objects.get(id=data["order"])
        neweb_pay_conf = settings.NEWEB_PAY

        payment_record = PaymentRecord(
            order=order,
            merchant_id=neweb_pay_conf["MerchantID"],
            description=data.get("description"),
        )
        payment_record.save()

        transaction_data = {
            "MerchantID": neweb_pay_conf["MerchantID"],
            "RespondType": "JSON",
            "TimeStamp": int(time.time()),
            "Version": neweb_pay_conf["Version"],
            "MerchantOrderNo": f"{neweb_pay_conf['MerchantID']}_{payment_record.id}",
            "Amt": order.amount,
            "ItemDesc": neweb_pay_conf["ItemDesc"],
            "NotifyURL": neweb_pay_conf["NotifyURL"],
            "ReturnURL": neweb_pay_conf["ReturnURL"],
            "Email": request.user.username,
        }

        # Encrypt payment info
        urlencode_translation_data = urllib.parse.urlencode(transaction_data)
        encrypted_data = encrypt_trade_info(
            urlencode_translation_data,
            neweb_pay_conf["HashKey"],
            neweb_pay_conf["HashIV"],
        )
        encrypted_data = encrypted_data.decode()

        # Prepare context-data
        _check_code = f"HashKey={neweb_pay_conf['HashKey']}&{encrypted_data}&HashIV={neweb_pay_conf['HashIV']}"
        hash_code = (
            hashlib.sha256(_check_code.encode("utf8")).hexdigest().upper()
        )
        context = {
            "MPG_GW": neweb_pay_conf["MPG_GW"],
            "HashKey": neweb_pay_conf["HashKey"],
            "MerchantID": neweb_pay_conf["MerchantID"],
            "TradeInfo": encrypted_data,
            "TradeSha": hash_code,
            "Amount": order.amount,
            "Version": neweb_pay_conf["Version"],
        }

        # Render payment page with context-data
        return render(request, "newebpay.html", context)


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
