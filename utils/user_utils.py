from rest_framework.authtoken.models import Token
from apps.users.models import User
from typing import Optional, Type, Union

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
