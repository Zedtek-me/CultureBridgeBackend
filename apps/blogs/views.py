from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.blogs.seriaizers import BlogSerializer
from utils.response_utils import ResponseManager




class BlogViewSet(ViewSet):
    """all things blog related"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """lists all blogs"""

    def create(self, request):
        """creates a blog"""
        serializer = BlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseManager.handle_success_response(
            message="blog successfully created!",
            status_code=201,
            data=serializer.data
        )
