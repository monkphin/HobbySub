import stripe
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates or updates the UserProfile
    and registers a Stripe customer if needed.
    """
    if created:
        try:
            # Step 1: Create the UserProfile
            profile = UserProfile.objects.create(user=instance)

            # Step 2: Create a Stripe Customer
            customer = stripe.Customer.create(
                email=instance.email,
                name=instance.username,
            )

            # Step 3: Save the Stripe ID in the profile
            profile.stripe_customer_id = customer.id
            profile.save()

            logger.info(f"Stripe customer created for {instance.username}: {customer.id}")
        
        except Exception as e:
            # Roll back profile creation if Stripe fails
            profile.delete()
            logger.error(f"Failed to create Stripe Customer for {instance.email}: {str(e)}")
    else:
        try:
            instance.profile.save()
        except Exception as e:
            logger.error(f"Failed to save profile for {instance.email}: {str(e)}")
