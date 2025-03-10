from django.contrib import admin

from apps.core.models import (
    Training, Course, TrainingCourse
)


class TrainingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "language", "status", "start_date", "end_date")
    list_filter = (
        "status", "language", "user", "start_date", "end_date"
    )

class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "description", "language_category", "created_at", "updated_at"
    )
    list_filter = (
        "title", "language_category", "created_at", "updated_at"
    )

class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ("training", "course", "user", "current_instructor_id")
    list_filter = ("training", "course", "user")


admin.site.register(Training, TrainingAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(TrainingCourse, TrainingCourseAdmin)
