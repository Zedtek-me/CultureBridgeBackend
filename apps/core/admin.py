from django.contrib import admin

from apps.core.models import Training, TrainingForm

admin.site.register((Training, TrainingForm))
