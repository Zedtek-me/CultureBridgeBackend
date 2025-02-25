from rest_framework import serializers
from apps.core.models import TrainingForm

from utils.validators import BaseValidator


class TrainingFormSerializer(serializers.ModelSerializer):
    self_description = serializers.JSONField(required=True)
    
    class Meta:
        model = TrainingForm
        exclude = ["user", "training", "created_at", "updated_at"]

    def validate_self_description(self, value):
        """validate the self description field"""
        BaseValidator.validate_self_description(value)
        return value

class TrainingDataSerializer(serializers.Serializer):
    no_of_students = serializers.IntegerField(required=True)
    including_me = serializers.BooleanField(required=True)
    self_description = serializers.JSONField(required=True)
    age_group = serializers.CharField(required=True)
    reason = serializers.CharField(required=True)
    personality = serializers.JSONField(required=True)
    confidence_level = serializers.CharField(required=True)
