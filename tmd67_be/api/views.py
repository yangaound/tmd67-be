from django.http import JsonResponse
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from tmd67_be.api.models import Path, Project
from tmd67_be.api.serializers import GroupSerializer, UserSerializer, PathSerializer, ProjectSerializer


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


def path_list(request):
    if request.method == 'GET':
        paths = Path.objects.all()
        serializer = PathSerializer(paths, many=True)
        return JsonResponse(serializer.data, safe=False)


def project_list(request):
    if request.method == 'GET':
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(serializer.data, safe=False)
