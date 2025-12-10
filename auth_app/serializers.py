from rest_framework import serializers
from auth_app.models import Person
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =[
            'first_name',
            'last_name',
            'username'
        ]
class PersonSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Person
        fields ='__all__'

class PersonGetOrCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.all()
    )
    position = serializers.CharField(max_length=64, required=False)
    description = serializers.CharField(required=False)