from django.contrib.auth.models import User
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.response import Response

from .models import Badge, Order, Ticket
from .serializers import (
    BadgeSerializer,
    CreateIdentitySerializer,
    OrderSerializer,
    RetrieveIdentitySerializer,
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


class TicketViewSet(viewsets.ModelViewSet):
    filterset_fields = ("chinese_name", "english_name")
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    filterset_fields = ("state", "user")
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class BadgeViewSet(viewsets.ModelViewSet):
    filterset_fields = ("first_name", "last_name", "order", "ticket", "club")
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
