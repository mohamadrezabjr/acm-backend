from rest_framework import serializers
from admin_panel_app.serializers.courses import AdminCourseParticipantSerializer
from auth_app.models import User
from admin_panel_app.serializers.events import AdminEventParticipantSerializer

class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="person.first_name")
    last_name = serializers.CharField(source="person.last_name")
    avatar = serializers.ImageField(source="person.avatar")
    student_id = serializers.CharField(source="person.student_id")

    class Meta:
        model = User

        fields = [
            "pk",
            "role",
            "phone",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "student_id",
        ]

class UserDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="person.first_name")
    last_name = serializers.CharField(source="person.last_name")
    avatar = serializers.ImageField(source="person.avatar")
    student_id = serializers.CharField(source="person.student_id")

    events = AdminEventParticipantSerializer(source="person.event_participants", many=True)
    courses = AdminCourseParticipantSerializer(source="person.course_participants", many=True)

    class Meta:
        model = User

        fields = [
            "pk",
            "role",
            "phone",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "student_id",
            "events",
            "courses",
        ]
