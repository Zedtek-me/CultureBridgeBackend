from django.contrib import admin
from apps.blogs.models import Blog
from apps.users.models import User

admin.site.register(Blog)
admin.site.register(User)
