from django.db import models

from interfaces.models import BaseModel
from utils.validators import BaseValidator

class Training(BaseModel):
    """contains the training information"""
    TRAINING_TYPE = (
        ('ONLINE', 'ONLINE'),
        ('OFFLINE', 'OFFLINE')
    )
    TRAINING_CHOICE = (
        ("PAID", "PAID"),
        ("FREE", "FREE")
    )
    LANGUAGE_CHOICE = (
        ("YORUBA", "YORUBA"),
        ("HAUSA", "HAUSA"),
        ("IGBO", "IGBO"),
        ("ENGLISH", "ENGLISH")
    )
    instructor = models.ForeignKey(
        to="users.User", on_delete=models.SET_NULL, null=True,
        related_name="instructor", related_query_name="instructor"
    )
    stundent = models.ForeignKey(
        to="users.User", on_delete=models.SET_NULL, null=True,
        related_name="student", related_query_name="student"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

class TrainingForm(BaseModel):
    """
    collects information about the training at signup
    """
    AGE_GROUP_CHOICES = (
        ("CHILD (5-8)", "CHILD (5-8)"),
        ("CHILD (9-12)", "CHILD 9-12"),
        ("TEENAGER (13-17)", "TEENAGER (13-17)"),
        ("ADULT (18-Above)", "ADULT (18-Above)")
    )
    PERSONALITY_TYPE_CHOICES = (
        ("INTROVERT", "INTROVERT"),
        ("EXTROVERT", "EXTROVERT"),
        ("AMBIVERT", "AMBIVERT")
    )
    CONFIDENCE_LEVEL_CHOICES = (
        ("BEGINNER", "BEGINNER"),
        ("INTERMEDIATE", "INTERMEDIATE")
    )

    no_of_students = models.IntegerField(null=True)
    including_me = models.BooleanField(null=True, default=False)
    user = models.ForeignKey(to="users.User", on_delete=models.CASCADE, null=True, blank=True)
    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES, default="ADULT (18-Above)", blank=True)
    reason = models.CharField(max_length=255, blank=True, help_text="why do you want to take this training")
    personality = models.CharField(max_length=50, choices=PERSONALITY_TYPE_CHOICES, default="INTROVERT", blank=True)
    self_description = models.JSONField(
        null=True, blank=True, default=list, help_text="Three words that best describe you",
        validators=[BaseValidator.validate_self_description]
    )
    confidence_level = models.CharField(
        max_length=255, blank=True,
        choices=CONFIDENCE_LEVEL_CHOICES,
        default="BEGINNER"
    )
    training = models.ForeignKey(
        to="Training", on_delete=models.CASCADE, null=True, blank=True
    )
