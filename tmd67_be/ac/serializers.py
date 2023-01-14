from rest_framework import serializers


class ReprMixin:
    @staticmethod
    def to_representation(instance):
        return {
            "identity": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
        }


class CreateIdentitySerializer(ReprMixin, serializers.Serializer):
    email = serializers.EmailField(help_text="*required")
    password = serializers.CharField(
        max_length=50, min_length=6, help_text="*required"
    )
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class RetrieveIdentitySerializer(ReprMixin, serializers.Serializer):
    identity = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
