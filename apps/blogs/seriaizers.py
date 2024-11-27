from rest_framework import serializers
from apps.blogs.models import Blog, Vlog
from apps.users.serializers import UserSerializer
from django.conf import settings
import logging

logger = logging.getLogger("root")

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url = serializers.SerializerMethodField(method_name="resolve_image_url")
    ENVIRONMENT_URL = settings.ENV_URL

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        blog = Blog.objects.create(**validated_data)
        if image:
            blog.image = image
            blog.save()
        return blog

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        blog = super().update(instance, validated_data)
        if image:
            blog.image = image
            blog.save()
        return blog

    def resolve_image_url(self, blog):
        """gets image url"""
        try:
            return self.ENVIRONMENT_URL + blog.image.url
        except (AttributeError, ValueError):
            return None




    class Meta:
        model = Blog
        fields = "__all__"

class VlogSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Vlog
        fields = "__all__"
