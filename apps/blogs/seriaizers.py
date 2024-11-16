from rest_framework import serializers
from apps.blogs.models import Blog, Vlog
from apps.users.serializers import UserSerializer

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = "__all__"

class VlogSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Vlog
        fields = "__all__"
