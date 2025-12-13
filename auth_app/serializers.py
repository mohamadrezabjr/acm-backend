from rest_framework import serializers
from auth_app.models import Person, valid_phone_ir
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
    first_name = serializers.CharField(max_length=128, required=False)
    last_name = serializers.CharField(max_length=128, required=False)
    position = serializers.CharField(max_length=64, required=False)
    bio = serializers.CharField(required=False)

class UserRegistrationSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[valid_phone_ir])
    password = serializers.CharField(write_only=True)
    student_id = serializers.CharField(max_length=10, required=False)
    first_name = serializers.CharField(max_length=128, required=False)
    last_name = serializers.CharField(max_length=128, required=False)
    email = serializers.EmailField(required=False)

    def validate_phone(self, value):
        if User.objects.filter(phone = value).exists():
            raise serializers.ValidationError('user with this phone already exists')
        return value
    def create(self, validated_data):
        print(validated_data)
        phone = validated_data.pop('phone')
        password = validated_data.pop('password')
        print(phone)
        user = User.objects.create(phone = phone)
        user.set_password(password)
        user.save()
        person = Person.objects.create(user = user, **validated_data)
        return user