from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response_utils import ResponseManager

from apps.users.models import User
from apps.users.serializers import UserSerializer



class UserViewSet(ViewSet):
    """viewset for all things user related"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """list users on the system"""
        users = User.objects.all()
        serialized = UserSerializer(users, many=True)
        return ResponseManager.handle_success_response(
            message="users retrieved successfully!",
            data=serialized.data
        )


class MailingViewSet(ViewSet):
    """viewset for all things mailing related"""
    permission_classes = []

    @action(detail=False, methods=["post"], url_path="newsletter-mail")
    def send_newsletter_mail(self, request):
        """sends newsletter mails to users"""

    @action(detail=False, methods=["post"], url_path="generic-mail")
    def send_generic_mail(self, request):
        """sends generic mails to users"""