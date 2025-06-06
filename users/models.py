"""
users/models.py

Defines the ShippingAddress model, which stores user-associated delivery
addresses for orders and subscriptions.
"""

from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text="The user this address belongs to."
    )
    recipient_f_name = models.CharField(
        max_length=30,
        blank=False,
        help_text="First name of the recipient."
    )
    recipient_l_name = models.CharField(
        max_length=30,
        blank=False,
        help_text="Last name of the recipient."
    )
    address_line_1 = models.CharField(
        max_length=60,
        blank=False,
        help_text="First line of the address "
        "(e.g., house number and street name)."
    )
    address_line_2 = models.CharField(
        max_length=60,
        blank=True,
        help_text="Additional address info e.g., apt or suit (optional)."
    )
    town_or_city = models.CharField(
        max_length=40,
        blank=False,
        help_text="City or town name."
    )
    county = models.CharField(
        max_length=50,
        blank=True,
        help_text="County, region or administrative area."
    )
    postcode = models.CharField(
        max_length=10,
        blank=False,
        help_text="Postal or ZIP code (varies by country)."
    )
    country = CountryField(
        blank_label="(Select country)",
        help_text="Select your country from the list."
    )
    phone_number = models.CharField(
        max_length=20,
        blank=False,
        help_text="Contact number for delivery issues."
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Check this box if this is your default delivery address"
    )
    is_gift_address = models.BooleanField(
        default=False,
        help_text="Check this box if this is an address used for a gift"
    )
    label = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. Home, Work, Parents"
    )

    def __str__(self):
        full_name = f"{self.recipient_f_name} {self.recipient_l_name}"
        return f"{full_name} — {self.postcode}"

    def can_be_deleted(self):
        """
        Check if the address is linked to active orders or subscriptions.
        """
        # Lazy import inside the method to avoid circular import
        from orders.models import Order, StripeSubscriptionMeta

        has_active_orders = Order.objects.filter(
            shipping_address=self,
            status__in=['pending', 'processing']
        ).exists()

        has_active_subscriptions = StripeSubscriptionMeta.objects.filter(
            shipping_address=self,
            cancelled_at__isnull=True
        ).exists()

        return not (has_active_orders or has_active_subscriptions)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
