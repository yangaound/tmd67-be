from rest_framework import serializers

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
        data["user"] = self.context["request"].user

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
        for instance in data["product_items"]:
            instance.save()

        if self.context["request"].method != "POST":
            self.context["view"].get_object().product_items.all().delete()

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
    transaction_identifier = serializers.CharField(
        max_length=255, read_only=True, allow_null=False, allow_blank=False
    )
    merchant_id = serializers.CharField(
        max_length=100, read_only=True, allow_null=False, allow_blank=False
    )
    status = serializers.CharField(
        max_length=40, read_only=True, allow_null=False, allow_blank=False
    )
    message = serializers.CharField(
        max_length=40, read_only=True, allow_null=False, allow_blank=False
    )
    result = serializers.CharField(
        max_length=512, read_only=True, allow_null=False, allow_blank=False
    )

    class Meta:
        model = PaymentRecord
        fields = "__all__"
