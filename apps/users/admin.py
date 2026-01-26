from django.contrib import admin
from apps.users.models import User, Profile, CampaignUser

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


class CampaignUserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name", "last_name", "email", "phone_number", "country",
        "campaign_source", "language", "created_at", "updated_at"
    )
    list_filter = (
        "country", "campaign_source", "language",
        "created_at", "updated_at"
    )
    search_fields = (
        "first_name__icontains", "last_name__icontains", "email__iexact", "phone_number__iexact",
        "country__icontains", "campaign_source__icontains"
    )

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CampaignUser, CampaignUserAdmin)