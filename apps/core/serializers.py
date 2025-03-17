from rest_framework import serializers
from apps.core.models import Training, PaymentTransaction

from utils.validators import BaseValidator


class TrainingSerializer(serializers.ModelSerializer):
    from apps.users.serializers import UserSerializer

    user = UserSerializer()
    class Meta:
        model = Training
        fields = "__all__"

class TrainingDataSerializer(serializers.Serializer):

    AGE_GROUP_CHOICES = (
        ("CHILD (5-8)", "CHILD (5-8)"),
        ("CHILD (9-12)", "CHILD 9-12"),
        ("TEENAGER (13-17)", "TEENAGER (13-17)"),
        ("ADULT (18-Above)", "ADULT (18-Above)")
    )

    PERSONALITY_TYPE_CHOICES = (
        ("INTROVERT", "INTROVERT"),
        ("EXTROVERT", "EXTROVERT"),
        ("AMBIVERT", "AMBIVERT")
    )
    CONFIDENCE_LEVEL_CHOICES = (
        ("BEGINNER", "BEGINNER"),
        ("INTERMEDIATE", "INTERMEDIATE")
    )
    language = serializers.ChoiceField(choices=Training.LANGUAGE_CHOICE, required=True)
    no_of_students = serializers.IntegerField(required=True)
    including_me = serializers.BooleanField(required=True)
    self_description = serializers.JSONField(
        required=True, validators=[BaseValidator.validate_self_description]
    )
    age_group = serializers.ChoiceField(choices=AGE_GROUP_CHOICES, required=True)
    reason = serializers.CharField(required=True)
    personality = serializers.ChoiceField(choices=PERSONALITY_TYPE_CHOICES, required=True)
    confidence_level = serializers.ChoiceField(choices=CONFIDENCE_LEVEL_CHOICES, required=True)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)


class AcceptPaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    email = serializers.EmailField(required=False)
    currency = serializers.ChoiceField(choices=PaymentTransaction.CURRENCY_CHOICES, default="NGN")
    user_id = serializers.CharField(required=False)
    training_id = serializers.CharField()
