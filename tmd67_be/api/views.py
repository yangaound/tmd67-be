from rest_framework import mixins, viewsets

from tmd67_be.api import models, serializers


class ListPathView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("tw_name", "en_name", "initialism")
    queryset = models.Path.objects.all()
    serializer_class = serializers.PathSerializer


class ListProjectView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("en_name", "tw_name")
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class ListLevelView(viewsets.GenericViewSet, mixins.ListModelMixin):
    filterset_fields = ("path", "project", "level", "is_elective")
    queryset = models.Level.objects.all()
    serializer_class = serializers.LevelSerializer
