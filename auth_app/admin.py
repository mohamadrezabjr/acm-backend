from django.contrib import admin
from auth_app.models import Person, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm , UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        ("User Information", {"fields": ("phone", "email", "password")}),
        ("User Status", {"fields": ("is_superuser", "is_admin", "is_creator", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        ("Create User", {"fields": ("phone", "email", "password", "confirm_password")}),
    )

    list_display = ["id", "phone", "email", "is_superuser", "is_admin", "is_creator"]
    list_filter = ["is_superuser", "is_admin", "is_creator"]
    search_fields = ["phone", "email"]
    ordering = ["-id"]
    filter_horizontal = ("groups", "user_permissions")

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            fieldsets = (
                ("User Status", {
                    "fields": ("phone", "email", "password", "is_superuser", "is_admin", "is_creator")
                }),
            )
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields["is_superuser"].disabled = True
            form.base_fields["is_admin"].disabled = True
            form.base_fields["is_creator"].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        is_created = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_created:
            Person.objects.create(user=obj)


admin.site.register(User, UserAdmin)
admin.site.register(Person)
