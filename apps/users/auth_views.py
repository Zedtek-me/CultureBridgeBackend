from django.db.transaction import atomic, on_commit

from utils.response_utils import ResponseManager
from utils.user_utils import UserUtils
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import permissions
from apps.users.serializers import UserSerializer, LoginSerializer


class AuthViewSet(ViewSet):
    """authentication viewset"""
    permission_classes = [ permissions.AllowAny ]

    @atomic
    @action(methods=["post"], detail=False, url_path="sign-up")
    def sign_up(self, request):
        """sign up view"""
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return ResponseManager.handle_error_response(
                message=serializer.error_messages,
                status_code=400
            )
        user = serializer.save()
        user.set_password(serializer.validated_data["password"])
        user.save()
        token = UserUtils.generate_auth_token(user)
        serializer.data["token"] = token
        return ResponseManager.handle_success_response(
            message="user successfully created!",
            status_code=201,
            data=serializer.data
        )

    @action(methods=["post"], detail=False, url_path="sign-in")
    def sign_in(self, request):
        """sign in view"""
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
            return ResponseManager.handle_success_response(
                message="email or password is incorrect!",
                status_code=400
            )
        token = UserUtils.generate_auth_token(user)
        serialized_data = UserSerializer(user)
        serialized_data.data["token"] = token
        return ResponseManager.handle_success_response(
            message="user successfully logged in!",
            status_code=200,
            data=serialized_data.data
        )
