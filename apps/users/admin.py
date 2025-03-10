from django.contrib import admin
from apps.users.models import User, Profile

class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "first_name", "last_name", "email", "username", "created_at",
        "updated_at"
    )
    list_filter = (
        "id", "first_name", "last_name", "email", "username",
        "created_at", "updated_at"
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "user_type", "language_taught", "phone_number", "country",
        "state", "city", "address", "created_at", "updated_at"
    )
    list_filter = (
        "user_type", "language_taught", "phone_number", "state", "city", "address",
        "created_at", "updated_at"
    )

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
