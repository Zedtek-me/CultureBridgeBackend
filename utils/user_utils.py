import logging

from rest_framework.authtoken.models import Token
from typing import Optional, Type, Union
from django.db.transaction import atomic, on_commit
from django.conf import settings

from utils.exception_utils import CustomException
from utils.core_utils import TrainingUtil
from utils.helpers import format_date_time

from apps.users.models import User, Profile
from apps.users.tasks import send_mail_async
from apps.core.models import Training

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
        phone_number = signup_info.pop("phone_number")
        if (User.objects.filter(email__iexact=signup_info.get("email")).exists() or
                User.objects.filter(username__iexact=signup_info.get("username")).exists()):
            raise CustomException("User with email or username already exists")
        user = User.objects.create_user(**signup_info)
        user.set_password(signup_info.get("password"))
        user.save()
        cls.update_user_profile(user, phone_number=phone_number, **kwargs)
        token = cls.generate_auth_token(user)
        if kwargs.get("referral_code"):
            cls._process_referral_code(user, kwargs.get("referral_code"))
        if training_info:
            cls._record_training_info(user, training_info)
        return user, token

    @classmethod
    def _process_referral_code(cls, user: User, referral_code: str):
        """processes referral code"""
        logger.debug("got into the process referral code block!!!!")
        pass

    @classmethod
    def _record_training_info(
        cls, user: User, training_info: dict, **kwargs
    ) -> Type[Training]:
        """records training info"""
        language = training_info.pop("language", "YORUBA")
        start_date = training_info.pop("start_date", None)
        start_time = training_info.pop("start_time")
        start_datetime = format_date_time(start_date, start_time)
        meta = training_info
        training_data = {
            "language": language,
            "start_date": start_datetime,
            "user": user,
            "meta": meta,
            "amount": TrainingUtil.get_training_cost(language=language)
        }
        training = TrainingUtil.create_training(**training_data)
        instructor_profile = Profile.objects.filter(
            user_type="INSTRUCTOR", language_taught__iexact=language.upper()
        ).first()
        instructor = (instructor_profile and instructor_profile.user)
        training.instructor_id = (instructor and instructor.id) or ""
        training.save()
        logger.debug(f"training info: {training}")
        # TODO: automatically match user with instructor the right instructor based on other criteria later
        return training

    @classmethod
    def update_user_profile(
        cls, user: Type[User], **kwargs
    ) -> Type[Profile]:
        user_type = kwargs.get("user_type")
        profile: Profile = user.profile
        profile.user_type = user_type
        profile.phone_number = kwargs.get("phone_number")
        profile.save()
        return profile

    @classmethod
    def get_user_type(cls, user: User) -> Optional[str]:
        """retrieves user"""
        return user.profile.user_type

    @classmethod
    def handle_marketing_signup(
        cls, data: dict
    ) -> None:
        """handles marketing signup info"""
        from apps.users.models import CampaignUser

        subject = "New Marketing Signup - Culturebridge"
        to_email = settings.MARKETING_TEAM_EMAILS
        template_name = "emails/marketing_signup.html"

        with atomic():
            campaign_user = CampaignUser.objects.create(**data)
            logger.debug(f"campaign user created: {campaign_user}")

            on_commit(
                lambda :
                # send email to admin and other stakeholders
                send_mail_async.delay(
                    subject=subject,
                    to_email=to_email,
                    template_name=template_name,
                    context=data,
                    from_email=settings.DEFAULT_FROM_EMAIL
                )
            )
