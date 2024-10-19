from django.db import models
from interfaces.models import BaseModel


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