"""
users/models.py

Defines the ShippingAddress model, which stores user-associated delivery addresses
for orders and subscriptions.
"""

# Django Imports
from django.db import models
from django.contrib.auth.models import User

class ShippingAddress(models.Model):
    """
    Represents a shipping address associated with a user account.

    Fields:
        user (ForeignKey): The user this address belongs to.
        recipient_f_name (str): First name of the recipient.
        recipient_l_name (str): Last name of the recipient.
        address_line_1 (str): First line of the address.
        address_line_2 (str, optional): Second line of the address (optional).
        town_or_city (str): Town or city name.
        county (str): County or region.
        postcode (str): Postal or ZIP code.
        country (str): Country name.
        phone_number (str): Contact number for delivery issues.
        is_default (bool): Whether this is the user's default address.
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             help_text="The user this address belongs to."
                             )
    recipient_f_name = models.CharField(max_length=100, 
                                      help_text="First name of the recipient."
                                      )
    recipient_l_name = models.CharField(max_length=100, 
                                      help_text="Last name of the recipient."
                                      )
    address_line_1 = models.CharField(max_length=80,
                                     help_text="First line of the address - eg house number and street name."
                                     )
    address_line_2 = models.CharField(max_length=80,
                                     blank=True,
                                     null=True,
                                     help_text="Additional address info eg apt or suit (optional)"
                                     )    
    town_or_city = models.CharField(max_length=40,
                                     help_text="City or town name."
                                     )
    county = models.CharField(max_length=80,
                                     help_text="County, region or administrative area."
                                     )
    postcode = models.CharField(max_length=20,
                                     help_text="Postal code or ZIP."
                                     )
    country = models.CharField(max_length=100,
                                     help_text="Country name from a list."
                                     )
    phone_number = models.CharField(max_length=20,
                                     help_text="Contact number for delivery issues."
                                     )
    is_default = models.BooleanField(default=False,
                                     help_text="Check this box if this is your default delivery address")
    
    def __str__(self):
        return f"{self.recipient_f_name} {self.recipient_l_name} — {self.postcode}"