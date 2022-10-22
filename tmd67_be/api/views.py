from rest_framework import mixins, viewsets

from tmd67_be.api import models, serializers


class ListPathView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("id", "tw_name", "en_name", "initialism")
    queryset = models.Path.objects.all()
    serializer_class = serializers.PathSerializer


class ListProjectView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("id", "en_name", "tw_name")
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class ListLevelView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("id", "path", "project",
                        "level", "is_elective", "is_old")
    queryset = models.Level.objects.all()
    serializer_class = serializers.LevelSerializer
