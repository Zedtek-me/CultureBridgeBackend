from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from interfaces.models import BaseModel

class User(BaseModel, AbstractUser):
    """custom user model"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} >>> {self.username}"
    