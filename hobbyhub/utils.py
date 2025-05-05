"""
Utility functions for common tasks across the project.

Includes helpers for:
- Flash messages (alert)
- Getting shipping addresses
- Building Shipping details
- Collecting metadata for gifts
- Display Sub Duration
- Display Sub Status

Import and use these anywhere you need a reusable function that keeps views
clean and DRY.
"""

# Django/External Imports
from dateutil.relativedelta import relativedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

PLAN_MAP = {
    settings.STRIPE_MONTHLY_PRICE_ID: (1, "Monthly"),
    settings.STRIPE_3MO_PRICE_ID: (3, "3-month plan"),
    settings.STRIPE_6MO_PRICE_ID: (6, "6-month plan"),
    settings.STRIPE_12MO_PRICE_ID: (12, "12-month plan"),
}


def alert(request, level, msg):
    """
    Flash a message to the user at the specified level using Django's messages
    framework.

    Args:
        request: The HttpRequest object.
        level (str): One of 'success', 'info', 'warning', 'error'.
        msg (str): The message text to display.

    Defaults to 'info' if an invalid level is given.
    """
    message_func = {
        "success": messages.success,
        "info": messages.info,
        "warning": messages.warning,
        "error": messages.error
    }.get(level, messages.info)

    user_info = (
        f"user={request.user}"
        if request.user.is_authenticated else "anon user"
    )
    logger.debug(f"Flashing {level} alert to {user_info}: {msg}")

    message_func(request, msg)


def get_user_default_shipping_address(request):
    """
    Retrieves the default shipping address for the logged-in user.

    If not found, redirects to the add address page with a warning.

    Returns:
        Tuple[ShippingAddress | None, HttpResponseRedirect | None]
    """
    shipping_address = request.user.addresses.filter(is_default=True).first()
    if not shipping_address:
        logger.warning(
            f"{request.user} has no default shipping address "
            "— redirecting to add_address"
        )
        alert(
            request,
            "error",
            "You must set a default shipping address before placing an order."
        )
        return None, redirect(f"{reverse('add_address')}?next={request.path}")
    return shipping_address, None


def build_shipping_details(shipping_address):
    """
    Build a shipping address dictionary for Stripe or shipping APIs.

    Args:
        shipping_address: A ShippingAddress instance.

    Returns:
        dict: Formatted shipping details.
    """
    return {
        'name': (
            f"{shipping_address.recipient_f_name} "
            f"{shipping_address.recipient_l_name}"
        ),
        'address': {
            'line1': shipping_address.address_line_1,
            'line2': shipping_address.address_line_2 or '',
            'city': shipping_address.town_or_city,
            'state': shipping_address.county,
            'postal_code': shipping_address.postcode,
            'country': shipping_address.country,
        }
    }


def get_gift_metadata(form, user_id, address_id=None):
    """
    Extracts gift-related metadata from a form.

    Args:
        form: Django Form object with cleaned_data.
        user_id: ID of the user sending the gift.
        address_id (int, optional): Selected shipping address ID.

    Returns:
        dict: Gift metadata for Stripe session.
    """
    metadata = {
        'recipient_name': form.cleaned_data.get('recipient_name'),
        'recipient_email': form.cleaned_data.get('recipient_email'),
        'sender_name': form.cleaned_data.get('sender_name'),
        'gift_message': form.cleaned_data.get('gift_message'),
        'user_id': str(user_id),
    }

    if address_id:
        metadata['shipping_address_id'] = str(address_id)

    return metadata



def get_subscription_duration_display(subscription):
    """
    Returns a human-readable string showing the subscription duration.

    Args:
        subscription: StripeSubscriptionMeta instance.

    Returns:
        str: e.g., "3-month plan – ends March 2025"
    """
    months, label = PLAN_MAP.get(subscription.stripe_price_id, (None, None))
    if not months:
        logger.warning(
            f"Unknown plan ID: {subscription.stripe_price_id} "
            f"for user {subscription.user}"
        )
        return "Unknown plan"

    end_date = subscription.created_at + relativedelta(months=months)
    return f"{label} – ends {end_date.strftime('%B %Y')}"


def get_subscription_status(sub):
    """
    Returns the current status of a subscription.

    Args:
        sub: StripeSubscriptionMeta instance or None.

    Returns:
        str: Status string (Active, Cancelled, or No subscription).
    """
    if not sub:
        return "No subscription"
    if sub.cancelled_at:
        return f"Cancelled on {sub.cancelled_at.strftime('%d %b %Y')}"
    return "Active"
