# users/signals.py

import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates or updates the UserProfile
    and registers a Stripe customer if needed.
    """
    if created:
        profile = UserProfile.objects.create(user=instance)

        # Create a Stripe Customer
        customer = stripe.Customer.create(
            email=instance.email,
            name=instance.username,
        )
        # Update the profile with Stripe ID
        profile.stripe_customer_id = customer.id
        profile.save()
        print(f"Stripe customer created for {instance.username}: {customer.id}")
    else:
        instance.profile.save()
