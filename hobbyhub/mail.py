"""
Handles plain text emailing for sending to users.
"""

from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.conf import settings

from .utils import PLAN_MAP


def send_user_email(subject, message, recipient_email):
    """
    Sends a plain text email using the configured backend.
    Assumes settings.py controls debug/production behavior.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )


# Registration
def send_registration_email(user):
    """Send welcome email after user registration."""
    send_mail(
        subject="Welcome to Hobby Hub!",
        message=(
            "Thanks for registering with Hobby Hub.\n"
            "We're excited to have you!\n\n"
            "Please confirm your email using the link we've just sent you. "
            "Once confirmed, you can continue your order here:\n"
            "http://127.0.0.1:8000/accounts/confirm-email/{{ token }}?next=/orders/select/?gift=true"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# Account details changed
def send_account_update_email(user):
    """Send email notification for profile updates."""
    send_user_email(
        subject="Your account details were updated",
        message=(
            f"Hi {user.username}, your profile information was changed."
        ),
        recipient_email=user.email
    )


# Successful single order
def send_order_confirmation_email(user, order_id):
    """Send order confirmation email."""
    send_user_email(
        subject="Order Confirmation",
        message=(
            f"Thanks for your order #{order_id}, it's now being processed."
        ),
        recipient_email=user.email
    )


# Gift (Sender)
def send_gift_confirmation_to_sender(user, recipient_email):
    """Send gift confirmation email to sender."""
    send_user_email(
        subject="Your gift is on its way!",
        message=(
            f"You sent a Hobby Hub box to {recipient_email}. "
            "We're sure they'll love it."
        ),
        recipient_email=user.email
    )


# Gift (Recipient)
def send_gift_notification_to_recipient(
        recipient_email,
        sender_name,
        gift_message
):
    """Notify recipient that a gift has been sent."""
    send_user_email(
        subject="You've received a gift from Hobby Hub!",
        message=(
            f"{sender_name} sent you a box!\n\n"
            f"Gift Message:\n{gift_message}"
        ),
        recipient_email=recipient_email
    )


# Address changed
def send_address_change_email(user, change_type="updated"):
    """Send notification for shipping address updates."""
    send_user_email(
        subject=f"Your shipping address was {change_type}",
        message=(
            f"Hi {user.username}, your shipping address was {change_type}."
        ),
        recipient_email=user.email
    )


# Account deleted
def send_account_deletion_email(email):
    """Confirm account deletion."""
    send_user_email(
        subject="Account Deleted",
        message=(
            "Your Hobby Hub account has been successfully deleted."
        ),
        recipient_email=email
    )


# Subscription started
def send_subscription_confirmation_email(user, plan_name):
    """Confirm subscription signup."""
    send_user_email(
        subject="Subscription Confirmed",
        message=(
            f"You're now subscribed to the {plan_name} plan. Welcome aboard!"
        ),
        recipient_email=user.email
    )


# Failed Payment
def send_payment_failed_email(user):
    """Notify user of failed subscription payment."""
    send_user_email(
        subject="Payment Failed",
        message=(
            f"Hi {user.username},\n\n"
            "Unfortunately, your recent payment attempt for your subscription "
            "failed. "
            "Please update your payment method to avoid interruptions."
        ),
        recipient_email=user.email
    )


# Upcoming renewal
def send_upcoming_renewal_email(user, renewal_date):
    """Notify user of upcoming subscription renewal."""
    send_user_email(
        subject="Your Hobby Hub renewal is coming up",
        message=(
            f"Hi {user.username},\n\n"
            "Your subscription is set to renew on "
            f"{renewal_date.strftime('%B %d, %Y')}.\n"
            "We'll charge your default payment method on file. "
            "No action is needed unless you'd like to make changes."
        ),
        recipient_email=user.email
    )


# Shipping Confirmation
def send_shipping_confirmation_email(user, box=None, tracking_number=None):
    """Confirm shipment of box."""
    box_name = box.name if box else "Hobby Hub"
    tracking_info = (
        f"\nTracking Number: {tracking_number}" if tracking_number else ""
    )
    send_user_email(
        subject="Your Hobby Hub box has shipped!",
        message=(
            f"Hi {user.username},\n\n"
            f"Your {box_name} box has shipped and is on its way!"
            f"{tracking_info}\n\n"
            "Thanks for being part of the Hobby Hub community."
        ),
        recipient_email=user.email
    )


# Cancellation Email
def send_subscription_cancelled_email(user, plan_id, start_date):
    """
    Notify user that their subscription has been cancelled.
    """
    months, label = PLAN_MAP.get(plan_id, (0, "Your plan"))
    end_date = start_date + relativedelta(months=months)

    send_user_email(
        subject="Subscription Cancelled",
        message=(
            f"Hi {user.username},\n\n"
            f"Your subscription to the {label} has been cancelled.\n"
            f"You’ll still receive your boxes through "
            f"{end_date.strftime('%B %Y')}.\n\n"
            "Thanks for being part of Hobby Hub!"
        ),
        recipient_email=user.email
    )
