import logging

from rest_framework.authtoken.models import Token
from typing import Optional, Type, Union
from django.db.transaction import atomic, on_commit

from utils.exception_utils import CustomException

from apps.users.models import User
from apps.core.models import TrainingForm, Training

logger = logging.getLogger("root")
class UserUtils:
    """all utils for user including authentication"""

    @classmethod
    def generate_auth_token(cls, user):
        """auth token generator"""
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    @classmethod
    def authenticate(cls, email: str, password: str)-> Optional[User]:
        """authenticates a user's credentials"""
        user = User.objects.filter(email__iexact=email).first()
        if user and user.check_password(password):
            return user
        return None

    @classmethod
    def signup_user(cls, **kwargs: dict) -> Optional[tuple]:
        """signs up a user"""
        signup_info = kwargs.pop("signup", {})
        training_info = kwargs.get("training_info", {})
        if (User.objects.filter(email=signup_info.get("email")).exists() or
                User.objects.filter(username=signup_info.get("username")).exists()):
            raise CustomException("User with email or username already exists")
        user = User.objects.create_user(**signup_info)
        user.set_password(signup_info.get("password"))
        user.save()
        token = cls.generate_auth_token(user)
        if signup_info.get("referral_code"):
            cls._process_referral_code(user, kwargs.get("referral_code"))
        cls._record_training_info(user, training_info)
        return user, token

    @classmethod
    def _process_referral_code(cls, user: User, referral_code: str):
        """processes referral code"""
        pass

    @classmethod
    def _record_training_info(
        cls, user: User, training_info: dict, **kwargs
    ) -> Type[TrainingForm]:
        """records training info"""
        training_info = TrainingForm.objects.create(**training_info)
        training_info.user = user
        training_info.save()
        logger.debug(f"training info: {training_info}")
        return training_info
