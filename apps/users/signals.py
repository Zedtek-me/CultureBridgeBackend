from django.db.models.signals import post_save

from apps.users.models import(
     User, Profile
)

def optionally_create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(optionally_create_user_profile, sender=User)
