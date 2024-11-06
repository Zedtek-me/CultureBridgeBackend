from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = "creates superuser accounts"
    user_creds = [
        {"email": "zechariahadebayo42@gmail.com", "password": "Zedtek1@culturebridge"}
    ]
    def register_user_in_db(self, creds: dict = dict):
        """registers users"""
        self.stdout.write(f"creating user:::: {creds}")
        return User.objects.create_superuser(**creds)

    def handle(self, *args, **kwargs):
        """creates super user"""
        users = list(map(self.register_user_in_db, self.user_creds))
        self.stdout.write(f"all users created:::: {users}")
