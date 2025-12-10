from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class UserCreationForm(forms.ModelForm):
    password = forms.CharField()
    confirm_password = forms.CharField()

    class Meta:
        model = User
        fields = ("phone",)

    def clean_confirm_password(self):
        cd = self.cleaned_data
        if cd["password"] and cd["confirm_password"] and cd["password"] != cd["confirm_password"]:
            raise ValidationError("Password do not match!!!")
        return cd["confirm_password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("phone", "password", "is_superuser","is_admin", "is_creator", "groups", "user_permissions")