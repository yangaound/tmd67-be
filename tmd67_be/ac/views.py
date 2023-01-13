from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import exceptions, generics, status, permissions

from .serializers import CreateIdentitySerializer, RetrieveIdentitySerializer


class ACIDRegister(generics.CreateAPIView):
    serializer_class = CreateIdentitySerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _tmp = User(**serializer.data)
        if User.objects.filter(email=_tmp.email).exists():
            raise exceptions.ValidationError({'email': ["Email was registered, please use forget password to reset."]})

        user = User(**serializer.data)
        user.username = _tmp.email
        user.set_password(_tmp.password)
        user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ACIDDirectory(generics.RetrieveAPIView):
    serializer_class = RetrieveIdentitySerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def retrieve(self, request, *args, **kwargs):
        return Response(self.serializer_class(request.user, context=self.get_serializer_context()).data)
