from django.contrib.auth.models import Group, User
from rest_framework import serializers

from tmd67_be.api.models import Path, Project


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = [
            "en_name",
            "tw_name",
            "initialism",
            "en_description",
            "tw_description",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "path",
            "level",
            "is_elective",
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
