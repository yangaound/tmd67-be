from rest_framework.serializers import ModelSerializer

from tmd67_be.api import models


class PathSerializer(ModelSerializer):
    class Meta:
        model = models.Path
        fields = [
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
            "en_name",
            "tw_name",
            "en_description",
            "tw_description",
            "en_purpose",
            "tw_purpose",
            "en_overview",
            "tw_overview",
            "includes",
            "evaluation_form",
        ]


class LevelSerializer(ModelSerializer):
    class Meta:
        model = models.Level
        fields = [
            "path",
            "project",
            "level",
            "is_elective",
        ]
