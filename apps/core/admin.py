from django.contrib import admin

from apps.core.models import (
    Training, Course, TrainingCourse,
    PaymentTransaction
)


class TrainingAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user_id", "status", "amount",
        "created_at", "updated_at"
    )
    list_filter = (
        "status", "user_id", "payment_status", "start_date", "end_date",
        "created_at", "updated_at"
    )
    search_fields = ("user_id__iexact", "language__icontains", "instructor_id__iexact")

class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "description", "language_category", "created_at", "updated_at"
    )
    list_filter = (
        "title", "language_category", "created_at", "updated_at"
    )

class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ("training", "course", "user", "current_instructor_id", "created_at", "updated_at")
    list_filter = ("training", "course", "user")


class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user_id", "training", "amount", "currency", "txn_reference",
        "status", "created_at", "updated_at"
    )
    list_filter = (
        "user_id", "training", "amount", "currency", "status", "created_at", "updated_at"
    )
    fields = [
        "training", "user_id", "amount", "currency", "description", "txn_reference", "status",
        "meta", "created_at", "updated_at"
    ]

admin.site.register(Training, TrainingAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(TrainingCourse, TrainingCourseAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
