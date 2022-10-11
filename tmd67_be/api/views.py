from rest_framework import mixins, viewsets

from tmd67_be.api.models import Path, Project
from tmd67_be.api.serializers import PathSerializer, ProjectSerializer


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
