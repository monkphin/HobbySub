"""
users/forms.py

Form classes related to user registration, password changes,
and managing shipping addresses.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Register(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=100,
        widget=forms.EmailInput(attrs={
            'maxlength': 100,
            'required': True,
            'autocomplete': 'email'
        }),
        help_text="Required. Enter a valid email address."
    )

    username = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'maxlength': 30,
            'required': True,
            'autocomplete': 'username'
        }),
        help_text=(
            "Required. 30 characters or fewer."
            "Letters, digits, and @/./+/-/_ only."
        )
    )

    first_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'maxlength': 30,
            'autocomplete': 'given-name'
        }),
        help_text="Optional. 30 characters or fewer."
    )

    last_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'maxlength': 30,
            'autocomplete': 'family-name'
        }),
        help_text="Optional. 30 characters or fewer."
    )

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'required': True,
            'autocomplete': 'new-password'
        }),
        help_text=(
            "Your password must meet the site's minimum security requirements."
        )
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'required': True,
            'autocomplete': 'new-password'
        }),
        help_text="Enter the same password again for confirmation."
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already registered.")
        return email
