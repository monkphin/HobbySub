"""
Handles plain text emailing for sending to users.
"""

from urllib.parse import urlencode

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import Signer
from django.urls import reverse

from .utils import PLAN_MAP

signer = Signer()


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
def send_registration_email(user, next_url=None):
    """Send welcome + confirmation email after registration."""
    token = signer.sign(user.pk)
    base_url = settings.SITE_URL + reverse('confirm_email', args=[token])
    confirmation_url = (
        f"{base_url}?{urlencode({'next': next_url})}"
        if next_url
        else base_url
    )

    message = (
        f"Hi {user.username},\n\n"
        "Thanks for registering with Hobby Hub!\n\n"
        "Please confirm your email by clicking the link "
        f"below:\n\n{confirmation_url}\n\n"
        "If you did not create this account, you can ignore this message."
    )

    send_user_email(
        subject="Confirm your Hobby Hub account",
        message=message,
        recipient_email=user.email
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


# Email address changed.
def send_email_change_notifications(user, old_email, new_email):
    """
    Notify both old and new email addresses about the email change.
    """
    # Notify the new email address
    send_user_email(
        subject="Your Hobby Hub account email was changed",
        message=(
            f"Hi {user.username},\n\n"
            "Your email address has been successfully updated "
            f"to {new_email}.\n\n"
            "If you did not perform this action, please contact support "
            "immediately."
        ),
        recipient_email=new_email
    )

    # Notify the old email address
    send_user_email(
        subject="Your Hobby Hub account email was changed",
        message=(
            f"Hi {user.username},\n\n"
            "The email address associated with your Hobby Hub account was "
            f"changed from {old_email} to {new_email}.\n\n"
            "If you did not perform this action, please contact support "
            "immediately."
        ),
        recipient_email=old_email
    )


# Password changed
def send_password_change_email(user):
    send_user_email(
        subject="Your password was changed",
        message=(
            f"Hi {user.username}, your password has been successfully changed."
        ),
        recipient_email=user.email
    )


# Password Reset
def send_password_reset_email(user, domain, protocol='https'):
    """
    Sends a password reset email to the user.
    Includes a link to reset their password, valid for a short time.
    """
    from django.contrib.auth.tokens import default_token_generator
    from django.urls import reverse
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url_path = reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token
        }
    )

    reset_link = f"{protocol}://{domain}{url_path}"

    message = (
        f"Hi {user.username},\n\n"
        "You requested a password reset for your Hobby Hub account.\n\n"
        f"Click the link below to reset your password:\n\n{reset_link}\n\n"
        "If you did not request this, ignore this email.\n\n"
        "Thanks,\n"
        "The Hobby Hub Team"
    )

    send_user_email(
        subject="Reset Your Hobby Hub Password",
        message=message,
        recipient_email=user.email
    )


# Successful single order
def send_order_confirmation_email(user, order_id):
    """Send order confirmation email."""
    send_user_email(
        subject=f"Order Confirmation - Order #{order_id}",
        message=(
            f"Thanks for your order #{order_id}, it's now being processed."
        ),
        recipient_email=user.email
    )


# Gift (Sender)
def send_gift_confirmation_to_sender(user, recipient_name):
    """Send gift confirmation email to sender."""
    send_user_email(
        subject="Your gift is on its way!",
        message=(
            f"You sent a Hobby Hub box to {recipient_name}. "
            "We're sure they'll love it."
        ),
        recipient_email=user.email
    )


# Gift (Recipient)
def send_gift_notification_to_recipient(
    recipient_email,
    sender_name,
    gift_message,
    recipient_name
):
    """Notify recipient that a gift has been sent."""
    send_user_email(
        subject="You've received a gift from Hobby Hub!",
        message=(
            f"Hi {recipient_name},\n\n"
            f"{sender_name} sent you a Hobby Hub box!\n\n"
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


# Auto archived box
def send_auto_archive_notification(box):
    """
    Sends an email notification to the admin when a box is auto-archived.
    """
    send_mail(
        'Box Auto-Archived',
        f'The box "{box.name}" has been auto-archived because '
        'its date is in the past.',
        settings.DEFAULT_FROM_EMAIL,
        ['admin@hobbysub.com'],
        fail_silently=False,
    )


def send_order_status_update_email(user, order_id, status):
    """
    Send an email notification to the user when their order status changes.
    """
    status_messages = {
        'pending': "Your order is currently pending and will be processed "
        "soon.",
        'processing': "Your order is now being processed.",
        'shipped': "Your order has been shipped and is on its way to you.",
        'cancelled': "Your order has been cancelled. If you have any "
        "questions, please contact support."
    }

    status_message = status_messages.get(
        status,
        "Your order status has been updated."
    )

    send_user_email(
        subject=f"Order Update - Order #{order_id}",
        message=(
            f"Hi {user.username},\n\n"
            f"{status_message}\n\n"
            "Thank you for choosing Hobby Hub.\n\n"
            "Best regards,\n"
            "The Hobby Hub Team"
        ),
        recipient_email=user.email
    )
