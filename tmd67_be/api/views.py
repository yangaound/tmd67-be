from django.contrib.auth.models import Group, User
from rest_framework import generics, mixins, permissions, viewsets

from tmd67_be.api.models import Path, Project
from tmd67_be.api.serializers import (GroupSerializer, PathSerializer,
                                      ProjectSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListPathView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = (
        "tw_name",
        "en_name",
        "initialism",
    )
    queryset = Path.objects.all()
    serializer_class = PathSerializer


class ListProjectView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("path", "level", "is_elective", "en_name", "tw_name")
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
