from django.db import models

class BaseModel(models.Model):
    """Base model for all other models for the app"""
    meta = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        get_latest_by = 'created_at'