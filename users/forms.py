from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm

from .models import ShippingAddress

class Register(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class ChangePassword(forms.Form):
    password1 = forms.CharField(
                                widget=forms.PasswordInput(attrs={'class': 'validate'}),
                                help_text="Confirm Password."
                                )
    password2 = forms.CharField(
                                widget=forms.PasswordInput(attrs={'class': 'validate'}),
                                help_text="Re-enter your new password."
                                )

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")

        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data
    
    def save(self, user):
        user.set_password(self.cleaned_data["password1"])
        user.save()

class AddAddressForm(forms.ModelForm):
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
                'is_billing'
                ]
        labels = {
                'recipient_f_name': 'First Name',
                'recipient_l_name': 'Last Name',
                'town_or_city': 'Town or City',
                'phone_number': 'Phone Number',
                'is_default': 'Set as my default shipping address',
                'is_billing': 'Set as my default billing address'
                }