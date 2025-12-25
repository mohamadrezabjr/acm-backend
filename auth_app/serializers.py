from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from auth_app.models import Person, valid_phone_ir
from django.contrib.auth import get_user_model

User = get_user_model()

class PersonSerializer(serializers.ModelSerializer):
    user = PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = Person
        fields ='__all__'

class PersonGetOrCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.all()
    )
    first_name = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)
    position = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True )
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def create(self, validated_data):
        id = validated_data.pop('id')
        if not id :
            person = Person.objects.create(**validated_data)
        else:
            person = Person.objects.filter(id=id).first()
        return person

class AuthMeSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    student_id =serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    person_id = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.person.first_name
    def get_last_name(self, obj):
        return obj.person.last_name
    def get_bio(self, obj):
        return obj.person.bio
    def get_student_id(self, obj):
        return obj.person.student_id
    def get_avatar(self, obj):
        if not obj.person.avatar:
            return None
        return obj.person.avatar.url
    def get_person_id(self, obj):
        if obj.person:
            return obj.person.id
        return None

    class Meta:
        model = User
        fields = [
            'phone',
            'person_id',
            'email',
            'id',
            'role',
            'first_name',
            'last_name',
            'bio',
            'student_id',
            'avatar'
        ]
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
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('user with this email already exists')
        return value
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = User.objects.create(phone = phone, email = email)
        user.set_password(password)
        user.save()
        person = Person.objects.create(user = user, **validated_data)
        return user