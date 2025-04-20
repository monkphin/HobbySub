"""
Utility functions for common tasks across the project.

Includes helpers for:
- Flash messages (alert)
- Getting shipping addresses. 
- Building Shipping details
- Collecting metadata for gifts
- Display Sub Duration
- Display Sub Status

Import and use these anywhere you need a reusable function that keeps views clean and DRY.
"""

from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from dateutil.relativedelta import relativedelta


PLAN_MAP = {
    settings.STRIPE_MONTHLY_PRICE_ID: (1, "Monthly"),
    settings.STRIPE_3MO_PRICE_ID: (3, "3-month plan"),
    settings.STRIPE_6MO_PRICE_ID: (6, "6-month plan"),
    settings.STRIPE_12MO_PRICE_ID: (12, "12-month plan"),
}


def alert(request, level, msg):
    """
    Flash a message to the user at the specified level using Django's messages framework.

    Args:
        request: The HttpRequest object.
        level (str): One of 'success', 'info', 'warning', 'error'.
        msg (str): The message text to display.

    Defaults to 'info' if an invalid level is given.
    """
    # Get the correct message function based on the level, defaulting to `info`
    message_func = {
        "success": messages.success,
        "info": messages.info,
        "warning": messages.warning,
        "error": messages.error
    }.get(level, messages.info)

    # Call the selected message function with the request and msg
    message_func(request, msg)


def get_user_default_shipping_address(request):
    """
    Retrieves the default shipping address for the logged-in user.
    If not found, redirects to the add address page with a warning.
    Returns a tuple: (ShippingAddress or None, redirect_response or None)
    """
    shipping_address = request.user.addresses.filter(is_default=True).first()
    if not shipping_address:
        alert(request, "error", "You must set a default shipping address before placing an order.")
        return None, redirect(f"{reverse('add_address')}?next={request.path}")
    return shipping_address, None


def build_shipping_details(shipping_address):
    return {
        'name': f'{shipping_address.recipient_f_name} {shipping_address.recipient_l_name}',
        'address': {
            'line1': shipping_address.address_line_1,
            'line2': shipping_address.address_line_2 or '',
            'city': shipping_address.town_or_city,
            'state': shipping_address.county,
            'postal_code': shipping_address.postcode,
            'country': shipping_address.country,
        }
    }


def get_gift_metadata(form, user_id):
    return {
        'recipient_name': form.cleaned_data.get('recipient_name'),
        'recipient_email': form.cleaned_data.get('recipient_email'),
        'sender_name': form.cleaned_data.get('sender_name'),
        'gift_message': form.cleaned_data.get('gift_message'),
        'user_id': str(user_id),
    }


def get_subscription_duration_display(subscription):
    months, label = PLAN_MAP.get(subscription.stripe_price_id, (None, None))
    if not months:
        return "Unknown plan"
    
    end_date = subscription.created_at + relativedelta(months=months)
    return f"{label} – ends {end_date.strftime('%B %Y')}"


def get_subscription_status(sub):
    if not sub:
        return "No subscription"
    if sub.cancelled_at:
        return f"Cancelled on {sub.cancelled_at.strftime('%d %b %Y')}"
    return "Active"
