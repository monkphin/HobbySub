from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import ShippingAddress

class Register(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

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
                'is_default'
                ]
        labels = {
                'recipient_f_name': 'First Name',
                'recipient_l_name': 'Last Name',
                'town_or_city': 'Town or City',
                'phone_number': 'Phone Number',
                'is_default': 'Set as my default shipping address'
                }