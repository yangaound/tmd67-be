from django.db import transaction
from rest_framework import exceptions, serializers

from .models import Order, PaymentRecord, ProductItem, Ticket, TicketProduct


class ReprMixin:
    @staticmethod
    def to_representation(instance):
        return {
            "id": instance.id,
            "account_identifier": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
        }


class CreateIdentitySerializer(ReprMixin, serializers.Serializer):
    email = serializers.EmailField(help_text="*required")
    password = serializers.CharField(
        max_length=50, min_length=6, help_text="*required"
    )
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class RetrieveIdentitySerializer(ReprMixin, serializers.Serializer):
    identity = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class TicketProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketProduct
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    state = serializers.CharField(max_length=10, read_only=True)
    amount = serializers.IntegerField(
        max_value=2147483647, min_value=0, read_only=True, default=0
    )
    created_time = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "state",
            "amount",
            "created_time",
            "updated_time",
            "product_items",
        ]

    def to_internal_value(self, data):
        data.pop("id", None)
        data.pop("state", None)
        data.pop("amount", None)
        data.pop("created_time", None)
        data.pop("updated_time", None)
        data["user"] = self.context["request"].user

        if data["product_items"] is None:
            raise exceptions.ValidationError(
                {"product_items": ["This field may not be null."]}
            )

        with transaction.atomic():
            data["product_items"] = [
                ProductItem(
                    ticket_product=TicketProduct.objects.get(
                        pk=item["ticket_product"]
                    ),
                    quantity=item["quantity"],
                )
                for item in data["product_items"]
            ]

            data["amount"] = sum(
                instance.quantity * instance.ticket_product.price
                for instance in data["product_items"]
            )

            if self.context["request"].method != "POST":
                self.context["view"].get_object().product_items.all().delete()

            for instance in data["product_items"]:
                instance.save()

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product_items"] = [
            ProductItemSerializer(item).data
            for item in instance.product_items.all()
        ]
        return data


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = "__all__"


class PaymentRecordSerializer(serializers.ModelSerializer):
    merchant_id = serializers.CharField(
        max_length=100, read_only=True, allow_null=False, allow_blank=False
    )
    respond_type = serializers.CharField(
        max_length=20, read_only=True, allow_null=False, allow_blank=False
    )
    version = serializers.CharField(
        max_length=20, read_only=True, allow_null=False, allow_blank=False
    )
    merchant_order_no = serializers.CharField(
        max_length=30, read_only=True, allow_null=False, allow_blank=False
    )
    status = serializers.CharField(
        max_length=20, read_only=True, allow_null=True, allow_blank=False
    )
    message = serializers.CharField(
        max_length=100, read_only=True, allow_null=True, allow_blank=False
    )
    result = serializers.JSONField(
        allow_null=True,
        read_only=True,
        style={"base_template": "textarea.html"},
    )

    class Meta:
        model = PaymentRecord
        fields = "__all__"
