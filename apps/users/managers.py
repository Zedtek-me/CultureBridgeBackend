from django.contrib.auth.models import BaseUserManager
from django.db.transaction import atomic


class UserManager(BaseUserManager):

    @atomic
    def create_user(self, **kwargs):
        if "email" not in kwargs:
            raise ValueError('Users must have an email address')
        user = self.model(**kwargs)
        user.set_password(kwargs.pop("password", ""))
        user.save()
        return user
        
    @atomic
    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.save()
