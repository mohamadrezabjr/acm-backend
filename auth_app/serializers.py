from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from django.contrib.auth.hashers import make_password
from auth_app.models import Person, valid_phone_ir, PendingRegistration
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['token_version'] = user.token_version

        return token

class PersonSerializer(serializers.ModelSerializer):
    user = PrimaryKeyRelatedField(required=False, read_only=True)
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def get_phone(self, obj):
        if not obj.user:
            return None
        return obj.user.phone
    def get_email(self, obj):
        if not obj.user:
            return None
        return obj.user.email
    class Meta:
        model = Person
        fields ='__all__'

class ProfileUpdateSerializer(serializers.ModelSerializer):
    user = PrimaryKeyRelatedField(required=False, read_only=True)
    phone = serializers.CharField(required=False, validators=[valid_phone_ir])

    def get_phone(self, obj):
        if not obj.user:
            return None
        return obj.user.phone

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists() and value != self.instance.user.phone:
            raise serializers.ValidationError("Phone already exists")
        return value

    def update(self, instance, validated_data):
        phone = validated_data.get("phone")
        if phone :
            instance.user.phone = phone
            instance.user.save()
        super().update(instance, validated_data)
        return instance

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
        if not obj.person:
            return None
        return obj.person.first_name
    def get_last_name(self, obj):
        if not obj.person:
            return None
        return obj.person.last_name
    def get_bio(self, obj):
        if not obj.person:
            return None
        return obj.person.bio
    def get_student_id(self, obj):
        if not obj.person:
            return None
        return obj.person.student_id
    def get_avatar(self, obj):
        if not obj.person or not obj.person.avatar:
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
    phone = serializers.CharField(validators=[valid_phone_ir], required=False, allow_blank=True, allow_null=True)
    hashed_password = serializers.CharField(write_only=True)
    student_id = serializers.CharField(max_length=10, required=False, allow_null=True)
    first_name = serializers.CharField(max_length=128, required=False, allow_null=True)
    last_name = serializers.CharField(max_length=128, required=False, allow_null=True)
    email = serializers.EmailField(required=False)

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('user with this phone already exists')
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('user with this email already exists')
        return value

    def create(self, validated_data):
        email = validated_data.pop('email')
        phone = validated_data.pop('phone', None)
        hashed_password = validated_data.pop('hashed_password')
        user = User.objects.create(phone = phone, email = email)
        user.password = hashed_password
        user.save()
        person = Person.objects.create(user = user, **validated_data)
        return user

class PendingRegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(validators=[valid_phone_ir], required=False, allow_null=True)
    class Meta:
        model = PendingRegistration
        fields = [
            'phone',
            'email',
            'password',
            'first_name',
            'last_name',
            'student_id',
        ]
    def validate_phone(self, value):
        if value and User.objects.filter(phone = value).exists():
            raise serializers.ValidationError('user with this phone already exists')
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('user with this email already exists')
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')

        hashed_password = make_password(raw_password)
        pending = PendingRegistration.objects.create(**validated_data, password = hashed_password)
        return pending