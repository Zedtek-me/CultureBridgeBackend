from django.db import models
from interfaces.models import BaseModel
from .managers import VlogManager


class Blog(BaseModel):
    """blog data schema"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "blogs"
        verbose_name = "blog"
        verbose_name_plural = "blogs"
        ordering = ('-created_at',)
        get_latest_by = 'created_at'


    def __str__(self):
        return f"{self.title} >>> {self.author}"

    
class Vlog(BaseModel):
    """vlog data schema"""
    title = models.CharField(max_length=255, null=True)
    url = models.URLField(null=True)
    uploaded_by = models.ForeignKey(
        to="users.User", on_delete=models.SET_NULL, null=True
    )

    objects = VlogManager()

    class Meta:
        db_table = "vlogs"
        verbose_name = "vlog"
        verbose_name_plural = "vlogs"
        ordering = ("-created_at", "title")
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.title} >>> {self.uploaded_by}"
