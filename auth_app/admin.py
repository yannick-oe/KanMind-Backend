"""Admin registration and forms for the custom user model."""

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User

PASSWORD_MISMATCH_ERROR = "The two password fields do not match."
PASSWORD_HELP_TEXT = (
    "Raw passwords are not stored, so there is no way to see this "
    "user's password. Use the change-password form to set it."
)


class UserCreationForm(forms.ModelForm):
    """Admin form that creates a user with a hashed password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "fullname")

    def clean_password2(self):
        """Ensure both password entries are present and equal."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not password1 or password1 != password2:
            raise forms.ValidationError(PASSWORD_MISMATCH_ERROR)
        return password2

    def save(self, commit=True):
        """Hash the chosen password and persist the user."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Admin form that edits a user and shows the password hash."""

    password = ReadOnlyPasswordHashField(
        label="Password", help_text=PASSWORD_HELP_TEXT
    )

    class Meta:
        model = User
        fields = (
            "email",
            "fullname",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Usable admin for the email-based custom user model."""

    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    ordering = ("id",)
    list_display = ("id", "email", "fullname", "is_staff", "is_active")
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "fullname")
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("fullname",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "fullname",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
