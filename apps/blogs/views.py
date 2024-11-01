from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.blogs.seriaizers import BlogSerializer
from apps.blogs.models import Blog
from utils.response_utils import ResponseManager





class BlogViewSet(ViewSet):
    """all things blog related"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """lists all blogs"""
        blogs = Blog.objects.all()
        serialized = BlogSerializer(blogs, many=True)
        return ResponseManager.handle_success_response(
            message="blogs retrieved successfully!",
            data=serialized.data
        )
    
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

    def delete(self, request, pk=None):
        """deletes a single blog object"""
        Blog.objects.filter(id=pk).delete()
        return ResponseManager.handle_success_response(
            message="blog deleted successfully!",
            data={}
        )
