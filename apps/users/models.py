from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from interfaces.models import BaseModel

from utils.validators import BaseValidator
from utils.helpers import logger

class User(BaseModel, AbstractUser):
    """custom user model"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} >>> {self.username}"


    @property
    def middle_name(self) -> str:
        """
        returns middle name if available, else empty string
        """
        names = self.first_name.split()
        if len(names) > 1:
            return " ".join(names[1:])
        return ""


class Profile(BaseModel):
    """profile model"""
    USER_TYPE_CHOICES = (
        ("STUDENT", "STUDENT"),
        ("INSTRUCTOR", "INSTRUCTOR")
    )
    LANGUAGE_CHOICE = (
        ("YORUBA", "YORUBA"),
        ("HAUSA", "HAUSA"),
        ("IGBO", "IGBO"),
        ("ENGLISH", "ENGLISH")
    )
    user = models.OneToOneField(to="users.User", on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(
        max_length=15, blank=True,
        validators=[
            BaseValidator.validate_phone_number
        ]
    )
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default="STUDENT")
    language_taught = models.CharField(choices=LANGUAGE_CHOICE, blank=True)


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


    @property
    def address_lines(self) -> tuple[str, str]:
        """returns address lines"""
        line1 = f"{self.address}, {self.city}"
        line2 = f"{self.state}, {self.country}"
        return line1, line2


    @property
    def phone_country_code(self) -> str:
        """returns the country code from the phone number"""
        country_code, _ = self.phone_number.split(" ", 1) if self.phone_number else ("", "")
        return country_code[1:] if country_code.startswith("+") else ""


    @property
    def phone_main_number(self) -> str:
        """returns the main number from the phone number"""
        _, main_number = self.phone_number.split(" ", 1) if self.phone_number else ("", "")
        return main_number if main_number else ""


class CampaignUser(BaseModel):
    """
    All users who sign up for marketing campaigns
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    campaign_source = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=50, choices=Profile.LANGUAGE_CHOICE, default="ENGLISH")
    age = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.email

    class Meta(BaseModel.Meta):
        db_table = "campaign_users"
        verbose_name = "campaign user"
        verbose_name_plural = "campaign users"
