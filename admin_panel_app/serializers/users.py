from rest_framework import serializers
from auth_app.models import User

class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="person.first_name")
    last_name = serializers.CharField(source="person.last_name")
    avatar = serializers.ImageField(source="person.avatar")
    student_id = serializers.CharField(source="person.student_id")

    class Meta:
        model = User

        fields = [
            "phone",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "student_id",
        ]