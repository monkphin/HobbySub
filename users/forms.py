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

# 25cal imports
from .models import ShippingAddress


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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email address is already in use.")
        return email


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
        phone = self.cleaned_data.get("phone_number", "").strip()

        # Must contain at least one digit
        if not re.search(r'\d', phone):
            raise ValidationError("Phone number must include at least one digit.")

        # Must only contain digits and common phone symbols
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise ValidationError("Phone number must only contain digits and symbols like +, -, (, ).")

        return phone
    
    def clean_postcode(self):
        postcode = self.cleaned_data.get("postcode", "").strip()
        if not re.match(r'^[\w\s-]+$', postcode):
            raise ValidationError("Enter a valid postal code using letters, numbers, or dashes.")
        return postcode
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


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Enter your email",
        widget=forms.EmailInput(attrs={'class': 'validate'})
    )


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'validate'})
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'validate'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")