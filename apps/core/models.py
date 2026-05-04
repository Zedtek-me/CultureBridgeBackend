from django.db import models
from django.utils import timezone

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
    STATUSES = (
        ("PENDING", "PENDING"),
        ("ONGOING", "ONGOING"),
        ("COMPLETED", "COMPLETED")
    )
    PAYMENT_STATUSES = TRAINING_CHOICE + (
        ("PARTIALLY_PAID", "PARTIALLY_PAID"),
        ("UNPAID", "UNPAID")
    )
    user = models.ForeignKey(
        to="users.User", on_delete=models.SET_NULL, null=True, blank=True,
        help_text="user who enrolled for the training"
    )
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICE, default="YORUBA")
    instructor_id = models.CharField(max_length=255, blank=True, help_text="instructor's id")
    status = models.CharField(max_length=50, choices=STATUSES, default="PENDING")
    payment_status = models.CharField(max_length=255, choices=PAYMENT_STATUSES, default="UNPAID", blank=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    amount = models.FloatField(
        null=True, default=0.0,
        help_text="amount to be paid for the training, if it's a paid training"
    )
    _choice = models.CharField(max_length=255, choices=TRAINING_CHOICE, default="PAID")
    _type = models.CharField(max_length=255, choices=TRAINING_TYPE, default="ONLINE")

    class Meta:
        verbose_name = "Training"
        verbose_name_plural = "Trainings"
        db_table = "trainings"

    def __str__(self):
        return f"{self.language} - {self.user.first_name}"

    @property
    def choice(self):
        return self._choice

    @property
    def type(self):
        return self._type

    @choice.setter
    def update_choice(self, val: str):
        self._choice = val
        self.save()

    @type.setter
    def update_type(self, val):
        self._type = val
        self.save()


class Course(BaseModel):
    """records all things courses"""
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    sub_modules = models.ForeignKey(
        to="self", on_delete=models.CASCADE, null=True, blank=True
    )
    language_category = models.CharField(
        max_length=255, blank=True, choices=Training.LANGUAGE_CHOICE
    )
    links = models.JSONField(default=list)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        db_table = "courses"

    def __str__(self):
        return f"{self.title} - {self.language_category}"

class TrainingCourse(BaseModel):
    """
    Pivot table for training and course
    """
    training = models.ForeignKey(to="Training", on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(to="Course", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(
        to="users.User", on_delete=models.CASCADE, null=True, blank=True,
        help_text="""
        who's taking the course.
        (The person who enrolled might not be the one taking the course)
        """
    )
    current_instructor_id = models.CharField(
        max_length=255, blank=True, help_text="instructor's id"
    )

    class Meta:
        verbose_name = "Training Course"
        verbose_name_plural = "Training Courses"
        db_table = "training_courses"


class PaymentTransaction(BaseModel):
    STATUSES = (
        ("PENDING", "PENDING"),
        ("FAILED", "FAILED"),
        ("SUCCESSFUL", "SUCCESSFUL")
    )
    CURRENCY_CHOICES = (
        ("NGN", "NGN"),
        ("USD", "USD")
    )
    training = models.ForeignKey(
        to="Training", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=255, choices=STATUSES, blank=True, default="PENDING")
    amount = models.FloatField(null=True)
    currency = models.CharField(max_length=255, choices=CURRENCY_CHOICES, default="USD", blank=True)
    description = models.TextField(blank=True)
    user_id = models.CharField(max_length=255, blank=True)
    txn_reference = models.CharField(max_length=255, blank=True, unique=True)

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        db_table = "payment_transaction"

class Assignment(BaseModel):
    """records assingments for trainings"""
    STATUSES = (
        ("PENDING", "PENDING"),
        ("COMPLETED", "COMPLETED")
    )
    training = models.ForeignKey(
        to="core.Training", on_delete=models.CASCADE
    )
    course_id = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    instructor_id = models.CharField(max_length=255, blank=True)
    user_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=255, blank=True, choices=STATUSES, default="PENDING")

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        db_table = "assignments"
        ordering = ("-created_at",)


class PaymentPlatformToken(BaseModel):
    TOKEN_SOURCES = [
        ("FLUTTERWAVE", "FLUTTERWAVE"),
        ("PAYSTACK", "PAYSTACK"),
        ("ANCHOR", "ANCHOR"),
        ("SQUAD", "SQUAD"),
        ("STRIPE", "STRIPE")
    ]
    token = models.TextField(null=True, blank=True)
    source = models.CharField(
        max_length=255, choices=TOKEN_SOURCES,
        default="FLUTTERWAVE", null=True, blank=True
    )
    expires_in = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(seconds=600)
    )


    class Meta(BaseModel.Meta):
        verbose_name = "payment platform token"
        verbose_name_plural = "payment platform tokens"
        db_table = "payment_platform_token"

    def __str__(self):
        return f"{self.source} <--> expires in {self.expires_in.min}"


    @classmethod
    def fetch_token_info(cls, platform: str):
        return cls.objects.filter(source__icontains=platform).first()



class CountryAsset(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "country asset"
        verbose_name_plural = "country assets"
        db_table = "country_asset"

    def __str__(self):
        return f"{self.name if self.name else self.country}"


    @classmethod
    def get_asset(
        cls, filter_params: dict, raise_exception: bool = False, *args, **kwargs
    ):
        """fetches country asset based on filter params"""
        from django.db.models import Q
        from utils.exception_utils import CustomException

        search_params = kwargs.get("search_filter", Q())
        asset = cls.objects.filter(search_params, **filter_params).first()
        if not asset and raise_exception:
            raise CustomException(
                "Asset not found for the specified country!"
                "please select another country or try again later!"
                ,
                status_code=404
            )
        return asset
