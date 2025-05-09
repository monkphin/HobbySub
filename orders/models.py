"""
orders/models.py

Defines database models for the orders app.
Includes models for subscription metadata, individual orders, and payments.
"""

from django.db import models
from django.contrib.auth.models import User
from users.models import ShippingAddress
from boxes.models import Box


class StripeSubscriptionMeta(models.Model):
    """
    Stores Stripe subscription metadata for a user, including the selected
    pricing tier, shipping address, and gift status.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    stripe_subscription_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    stripe_price_id = models.CharField(max_length=100)
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    is_gift = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.stripe_subscription_id or 'No Sub ID'}"
        )


class Order(models.Model):
    """
    Represents an individual order placed by a user.
    Includes shipping info, related box, Stripe reference, and status.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )
    box = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    order_date = models.DateField(auto_now_add=True)
    scheduled_shipping_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class Payment(models.Model):
    """
    Records payments made against orders, including amount, method,
    and payment status.
    """
    PAYMENT_STATUS = [
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    payment_method = models.CharField(max_length=50)
    payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)


    def __str__(self):
        return f"Payment #{self.id} - {self.status}"
