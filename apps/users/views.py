from rest_framework.viewsets import ViewSet
from rest_framework import status
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
