"""
users/forms.py

Form classes related to user registration, password changes,
and managing shipping addresses.
"""

from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django_countries.widgets import CountrySelectWidget

from .models import ShippingAddress

class CustomSignupForm(SignupForm):
    username = forms.CharField(
        max_length=50,
        label="Username",
        required=True,
        help_text="Pick a unique name (max 50 characters)"
    )
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        return user


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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.user.check_password(cleaned_data.get("current_password")):
            self.add_error('current_password', "Current password is incorrect.")
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error('password2', "New passwords do not match.")
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class AddAddressForm(forms.ModelForm):
    """
    Form for adding or editing a shipping address.
    """
    class Meta:
        model = ShippingAddress
        fields = [
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
            'recipient_f_name': 'First Name',
            'recipient_l_name': 'Last Name',
            'town_or_city': 'Town or City',
            'phone_number': 'Phone Number',
            'is_default': 'Set as my default shipping address',
        }
        widgets = {
            'country': CountrySelectWidget(attrs={'class': 'browser-default'}),
            'is_default': forms.CheckboxInput(),
        }
