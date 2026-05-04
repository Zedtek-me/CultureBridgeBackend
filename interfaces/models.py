from django.db import models

class BaseModel(models.Model):
    """Base model for all other models for the app"""
    meta = models.JSONField(default=dict, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        get_latest_by = 'created_at'

    def update_self(self, data: dict) -> models.Model:
        """
        updates data on the instanace of the model.
        """
        for k, v in data.items():
            if hasattr(self, k) and v is not None:
                setattr(self, k, v)
        self.save()
        return self
