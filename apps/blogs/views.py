from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from django.db import transaction
from apps.blogs.seriaizers import BlogSerializer, VlogSerializer
from apps.blogs.models import Blog, Vlog
from apps.blogs.permissions.is_authenticated import IsAuthenticated
from utils.response_utils import ResponseManager
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)






class BlogViewSet(ViewSet):
    """all things blog related"""
    permission_classes = [AllowAny]

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
        serializer.save()
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
        blog_serializer.save()
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


class VlogViewSet(ViewSet):
    """all things vlog related"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @transaction.atomic
    @action(methods=["post"], detail=False, url_path="upload-video")
    def upload_video(self, request):
        """uploads a video"""
        video_serializer = VlogSerializer(data=request.data, partial=True)
        video_serializer.is_valid(raise_exception=True)
        video_serializer.save()
        return ResponseManager.handle_success_response(
            message="video uploaded successfully!",
            data=video_serializer.data,
            status_code=201
        )

    def list(self, request):
        """lists all vlogs"""
        fc_user = request.query_params.get("fc_user")
        _filter_args = {}
        if fc_user:
            _filter_args["owner"] = request.user
        vlogs = Vlog.objects.all_vlogs(**_filter_args)
        serializer = VlogSerializer(vlogs, many=True)
        return ResponseManager.handle_success_response(
            message="vlogs retrieved successfully!",
            data=serializer.data
        )
