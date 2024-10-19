from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class BlogViewSet(ViewSet):
    """all things blog related"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """lists all blogs"""
        