from django.db.transaction import atomic, on_commit
from django.conf import settings
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework import status

from utils.response_utils import ResponseManager
from utils.user_utils import UserUtils
from utils.helpers import get_logger
from utils.emial_utils import EmailUtil

from apps.users.serializers import (
    UserSerializer, LoginSerializer,
    CombinedAuthSerializer, MarketingSignupSerializer

)

logger = get_logger()

class AuthViewSet(ViewSet):
    """authentication viewset"""
    permission_classes = [ permissions.AllowAny ]

    @atomic
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        """signup a user"""
        serializer = CombinedAuthSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        validated_data = serializer.validated_data
        user, token = UserUtils.signup_user(**validated_data)
        user_serializer = UserSerializer(user)
        return ResponseManager.handle_success_response(
            message="user signed up successfully!",
            data={"token": token, **(user_serializer.data)}
        )


    @action(methods=["post"], detail=False, url_path="login")
    def sign_in(self, request):
        """sign in view"""
        try:
            serializers = LoginSerializer(data=request.data)
            if not serializers.is_valid(raise_exception=False):
                return ResponseManager.handle_error_response(
                    message=serializers.error_messages,
                    status_code=400
                )
            user = UserUtils.authenticate(
                email=serializers.validated_data.get("email"),
                password=serializers.validated_data.get("password")
            )
            if not user:
                return ResponseManager.handle_error_response(
                    message="email or password is incorrect!",
                    status_code=400
                )
            token = UserUtils.generate_auth_token(user)
            serialized_data = UserSerializer(user)
            return ResponseManager.handle_success_response(
                message="user successfully logged in!",
                status_code=200,
                data={"token": token, **serialized_data.data}
            )
        except Exception as e:
            logger.exception(f"exception occured during logging in: {e}")
            return ResponseManager.handle_error_response(
                message="Error occured during sign in. Try again later or contact admin!",
                status_code=500
            )

    @action(methods=["post"], detail=False, url_path="marketing-form-info")
    def handle_marketing_info(self, request):
        """
        gets the information collected through marketing form;
        then send it through email to the admin and other stake holders.
        """
        serializer = MarketingSignupSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        validated_data = serializer.validated_data
        # Send email to admin and stakeholders
        subject = "New Marketing Signup"
        to_email = settings.MARKETING_TEAM_EMAILS
        template_name = "emails/marketing_signup.html"
        email_sent = EmailUtil.send_templated_email(
            subject=subject,
            to_email=to_email,
            template_name=template_name,
            context=validated_data
        )
        logger.debug(f"email sent::: {email_sent}")
        if not email_sent:
            return ResponseManager.handle_error_response(
                message="Failed to send marketing signup email.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return ResponseManager.handle_success_response(
            message="Marketing signup information submitted successfully.",
            status_code=status.HTTP_200_OK
        )
