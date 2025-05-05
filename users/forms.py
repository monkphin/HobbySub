"""
users/forms.py

Form classes related to user registration, password changes,
and managing shipping addresses.
"""

# Django/Remote imports
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django import forms
import re


# Local imports
from .models import ShippingAddress


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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
        help_text="Required. 30 characters or fewer. Letters, digits, and @/./+/-/_ only."
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
        help_text="Your password must meet the site's minimum security requirements."
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



class ChangePassword(forms.Form):
    """
    Custom form for setting a new password with confirmation.
    """
    current_password = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'validate'}),
            help_text="Enter your current password."
        )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'validate'}),
        help_text="Enter your new password."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'validate'}),
        help_text="Re-enter your new password."
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Pass user in view
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")

        if self.user and not self.user.check_password(current_password):
            self.add_error(
                'current_password',
                "Current password is incorrect."
            )

        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', "New passwords do not match.")

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name'
        ]


class AddAddressForm(forms.ModelForm):
    """
    Form for adding or editing a shipping address.
    """
    # Add this line to include a checkbox in the form
    is_gift_address = forms.BooleanField(
        required=False,
        label="This is a gift recipient address"
    )
    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise ValidationError("Phone number must only contain digits and common symbols (+, -, (, )).")
        return phone

    class Meta:
        model = ShippingAddress
        fields = [
            'label',
            'recipient_f_name',
            'recipient_l_name',
            'address_line_1',
            'address_line_2',
            'town_or_city',
            'county',
            'postcode',
            'country',
            'phone_number',
            'is_default',
        ]
        labels = {
            'label': 'Label (e.g. Home, Work)',
            'recipient_f_name': 'First Name',
            'recipient_l_name': 'Last Name',
            'town_or_city': 'Town or City',
            'phone_number': 'Phone Number',
            'is_default': 'Set as my default shipping address',
        }
        widgets = {
            'country': CountrySelectWidget(
                attrs={'class': 'browser-default'}
            ),
            'is_default': forms.CheckboxInput(),
        }
