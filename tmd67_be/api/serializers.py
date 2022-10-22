from rest_framework.serializers import ModelSerializer

from tmd67_be.api import models


class PathSerializer(ModelSerializer):
    class Meta:
        model = models.Path
        fields = [
            "id",
            "en_name",
            "tw_name",
            "initialism",
            "en_description",
            "tw_description",
        ]


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = models.Project
        fields = [
            "id",
            "en_name",
            "tw_name",
            "en_description",
            "tw_description",
            "en_purpose",
            "tw_purpose",
            "en_overview",
            "tw_overview",
            "en_includes",
            "tw_includes",
            "en_form",
            "tw_form",
        ]


class LevelSerializer(ModelSerializer):
    class Meta:
        model = models.Level
        fields = [
            "id",
            "path",
            "project",
            "level",
            "is_elective",
            "is_old",
        ]
