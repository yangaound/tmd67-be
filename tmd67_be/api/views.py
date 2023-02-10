from rest_framework import mixins, viewsets

from tmd67_be.api import models, serializers


class ListPathView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    lookup_field = "show_name"
    filterset_fields = ("id", "tw_name", "en_name", "show_name", "initialism")
    queryset = (
        models.Path.objects.prefetch_related("levels", "levels__project")
        .order_by("id")
        .all()
    )
    serializer_class = serializers.PathSerializer


class ListProjectView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    lookup_field = "show_name"
    filterset_fields = ("id", "en_name", "tw_name", "show_name")
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class ListClubView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    filterset_fields = ("chinese_name", "english_name")
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer
