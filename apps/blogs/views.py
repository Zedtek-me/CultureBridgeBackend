from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import transaction
from apps.blogs.seriaizers import BlogSerializer
from apps.blogs.models import Blog
from apps.blogs.permissions.is_authenticated import IsAuthenticated
from utils.response_utils import ResponseManager
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)






class BlogViewSet(ViewSet):
    """all things blog related"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """lists all blogs"""
        blogs = Blog.objects.all()
        serialized = BlogSerializer(blogs, many=True)
        return ResponseManager.handle_success_response(
            message="blogs retrieved successfully!",
            data=serialized.data
        )

    @transaction.atomic
    def create(self, request):
        """creates a blog"""
        logger.debug(f"user from request: {request.user}")
        serializer = BlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return ResponseManager.handle_success_response(
            message="blog successfully created!",
            status_code=201,
            data=serializer.data
        )

    def retrieve(self, request, pk=None):
        """returns a single blog object"""
        blog = Blog.objects.filter(id=pk).first()
        if not blog:
            return ResponseManager.handle_error_response(
                message="blog not found!",
                status_code=404
            )
        return ResponseManager.handle_success_response(
            message="blog retrieved successfully!",
            data=BlogSerializer(blog).data
        )

    @transaction.atomic
    def update(self, request, pk=None):
        """updates a blog"""
        blog = Blog.objects.get(id=pk)
        blog_serializer = BlogSerializer(blog, data=request.data, partial=True)
        blog_serializer.is_valid(raise_exception=True)
        return ResponseManager.handle_success_response(
            message="blog updated successfully!",
            data=blog_serializer.data
        )

    @transaction.atomic
    def delete(self, request, pk=None):
        """deletes a single blog object"""
        Blog.objects.filter(id=pk).delete()
        return ResponseManager.handle_success_response(
            message="blog deleted successfully!",
            data={}
        )
