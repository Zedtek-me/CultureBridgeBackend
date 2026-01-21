import logging

from typing import (
    Optional, Union, Any
)
from django.core.exceptions import ValidationError

from rest_framework import serializers
from apps.users.models import User, Profile

from utils.user_utils import UserUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id","password", "email", "first_name", "last_name", "username", "meta", "user_type"]

    def get_user_type(self, obj):
        try:
            return UserUtils.get_user_type(obj)
        except (Profile.DoesNotExist, ValidationError, Exception) as e:
            logging.exception("Error getting user type: %s", e)
            return None

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

class SignupSerializer(LoginSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=False, write_only=True)
    phone_number = serializers.CharField(required=False, write_only=True)
    password = serializers.CharField(required=False, write_only=True)

class CombinedAuthSerializer(serializers.Serializer):
    from apps.core.serializers import TrainingDataSerializer

    USER_TYPE_CHOICES = (
        ("STUDENT", "STUDENT"),
        ("INSTRUCTOR", "INSTRUCTOR")
    )
    signup = SignupSerializer(required=False)
    login = LoginSerializer(required=False)
    training_info = TrainingDataSerializer(required=False)
    referral_code = serializers.CharField(required=False, write_only=True)
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES, required=False, write_only=True)


class MarketingSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    country = serializers.CharField()
    age = serializers.CharField()
    language = serializers.CharField()
    phone_number = serializers.CharField(required=False)
