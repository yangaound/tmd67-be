from rest_framework.serializers import ModelSerializer

from tmd67_be.api import models


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = models.Project
        fields = [
            "id",
            "en_name",
            "tw_name",
            "show_name",
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
        depth = 1
        model = models.Level
        fields = [
            "level",
            "en_name",
            "is_elective",
            "is_old",
            "project",
        ]


class PathSerializer(ModelSerializer):
    class Meta:
        model = models.Path
        fields = [
            "id",
            "en_name",
            "tw_name",
            "show_name",
            "initialism",
            "en_description",
            "tw_description",
        ]

    def to_representation(self, instance):
        path = super().to_representation(instance)
        path["levels"] = [
            LevelSerializer(instance=v).data for v in instance.levels.all()
        ]
        return path
