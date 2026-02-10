import re
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_integer
from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from auth_app.managers import UserManager
from auth_app.utils import generate_random_otp
from django.utils import timezone

def valid_phone_ir(value):
    pattern = r'^09\d{9}$'
    if not re.match(pattern , value) or len(value) != 11:
        raise ValidationError("phone number is not valid")
    return value

class User(PermissionsMixin, AbstractBaseUser):
    phone = models.CharField(max_length = 11, validators=[validate_integer, valid_phone_ir], unique = True, null=True)
    is_admin = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def role(self):
        if self.is_admin or self.is_superuser:
            return "admin"
        if self.is_creator:
            return "creator"
        return "user"

    objects = UserManager()

    def __str__(self):
        return self.email

class Person(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    position = models.CharField(max_length=64, null=True, blank = True)
    bio = models.TextField(null = True, blank=True)
    student_id = models.CharField(max_length=10, blank = True, null= True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} : {self.user}"

class PendingRegistration(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    phone = models.CharField(max_length=11, validators=[validate_integer, valid_phone_ir], null=True, blank=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    first_name= models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    student_id = models.CharField(max_length=10, blank = True, null= True)
    otp = models.CharField(max_length=6, default=generate_random_otp, null = True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expiration_time = models.DurationField(default=timezone.timedelta(minutes=7))
    revalidation_time = models.DurationField(default=timezone.timedelta(minutes=2))

    @property
    def is_expired(self):
        return (timezone.now()  - self.updated_at) > self.expiration_time
    @property
    def can_revalidate(self):
        return (timezone.now()  - self.updated_at) > self.revalidation_time
    @property
    def remaining_revalidation_time(self):
        remaining = self.revalidation_time - (timezone.now()  - self.updated_at)
        return max(remaining, timezone.timedelta(0))

    def revalidate(self):
        self.otp = generate_random_otp()
        self.save()