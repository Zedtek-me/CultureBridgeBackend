from rest_framework import serializers
from apps.core.models import (
    Training, PaymentTransaction,
    Course, TrainingCourse, Assignment
)

from utils.validators import BaseValidator
from utils.core_utils import TrainingUtil
from utils.user_utils import UserUtils


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"

class TrainingSerializer(serializers.ModelSerializer):
    from apps.users.serializers import UserSerializer

    user = UserSerializer()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Training
        exclude = ["_choice", "_type"]

    def get_courses(self, obj):
        """returns the courses that have been assigned to this training"""
        course_ids = TrainingCourse.objects.filter(training__id=obj.id).\
            values_list("course__id", flat=True)
        return CourseSerializer(
            Course.objects.filter(id__in=course_ids), many=True
        ).data

class TrainingDataSerializer(serializers.Serializer):

    AGE_GROUP_CHOICES = (
        ("CHILD (5-8)", "CHILD (5-8)"),
        ("CHILD (9-12)", "CHILD 9-12"),
        ("TEENAGER (13-17)", "TEENAGER (13-17)"),
        ("ADULT (18-ABOVE)", "ADULT (18-ABOVE)")
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
    language = serializers.ChoiceField(choices=Training.LANGUAGE_CHOICE, required=True)
    no_of_students = serializers.IntegerField(required=True)
    including_me = serializers.BooleanField(required=True)
    self_description = serializers.JSONField(
        required=True, validators=[BaseValidator.validate_self_description]
    )
    age_group = serializers.ChoiceField(choices=AGE_GROUP_CHOICES, required=True)
    reason = serializers.CharField(required=True)
    personality = serializers.ChoiceField(choices=PERSONALITY_TYPE_CHOICES, required=True)
    confidence_level = serializers.ChoiceField(choices=CONFIDENCE_LEVEL_CHOICES, required=True)
    start_date = serializers.DateField(required=False)
    start_time = serializers.CharField(required=False, write_only=True)
    end_date = serializers.TimeField(required=False)


class AcceptPaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    email = serializers.EmailField(required=False)
    currency = serializers.ChoiceField(choices=PaymentTransaction.CURRENCY_CHOICES, default="NGN")
    user_id = serializers.CharField(required=False)
    training_id = serializers.CharField()

class TrainingMetrics(serializers.Serializer):
    total_trainings = serializers.IntegerField()
    completed_trainings = serializers.IntegerField()
    in_progress_trainings = serializers.IntegerField()
    pending_trainings = serializers.IntegerField()
    free_trainings = serializers.IntegerField()
    paid_trainings = serializers.IntegerField()
    total_students = serializers.SerializerMethodField()

    def get_total_students(self, obj: Training) -> int:
        """gets the total no of students taken, in case the current user is an instructor"""
        user = self.context.get("user")
        if UserUtils.get_user_type(user) == "INSTRUCTOR":
            return TrainingUtil.get_total_instructor_students(
                instructor_id=user.id
            )
        return 0


class AssignCourseSerializer(serializers.Serializer):
    training_id = serializers.IntegerField()
    course_ids = serializers.ListField(child=serializers.IntegerField())


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class CreateAssignmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    due_date = serializers.DateTimeField(required=False)
    course_id = serializers.CharField()
    training_id = serializers.CharField()

class UpdateAssignmentSerializer(CreateAssignmentSerializer, serializers.Serializer):
    assignment_id = serializers.CharField()
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    course_id = serializers.CharField(required=False)
    training_id = serializers.CharField(required=False)
    answer = serializers.CharField(required=False, max_length=5000)
    update_src = serializers.CharField(required=False, write_only=True)
    status = serializers.ChoiceField(
        choices=Assignment.STATUSES, required=False
    )

    def validate_assignment_id(self, value):
        """validates that the assignment id exists"""
        if not Assignment.objects.filter(id=value).exists():
            raise serializers.ValidationError("Assignment does not exist")
        return value

class MarkAttendanceSerializer(serializers.Serializer):
    training_id = serializers.IntegerField(required=False)
    course_id = serializers.IntegerField()
    extra_note = serializers.CharField(required=False, max_length=255)

class ImageLinkSerializer(serializers.Serializer):
    src = serializers.CharField(max_length=255)
    link = serializers.CharField(max_length=5000, required=False)
    height = serializers.CharField(required=False)
    width = serializers.CharField(required=False)
    type = serializers.CharField(max_length=255)

class CreateCourseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    language_category = serializers.CharField(max_length=255)
    images = serializers.ListField(child=ImageLinkSerializer())
