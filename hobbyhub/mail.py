from django.core.mail import send_mail
from django.conf import settings

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
    send_mail(
        subject="Welcome to Hobby Hub!",
        message="Thanks for registering with Hobby Hub. We're excited to have you!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# Account details changed
def send_account_update_email(user):
    send_user_email(
        subject="Your account details were updated",
        message=f"Hi {user.username}, your profile information was changed.",
        recipient_email=user.email
    )


# Successful single order
def send_order_confirmation_email(user, order_id):
    send_user_email(
        subject="Order Confirmation",
        message=f"Thanks for your order #{order_id}, it's now being processed.",
        recipient_email=user.email
    )


# Gift (Sender)
def send_gift_confirmation_to_sender(user, recipient_email):
    send_user_email(
        subject="Your gift is on its way!",
        message=f"You sent a Hobby Hub box to {recipient_email}. They'll love it.",
        recipient_email=user.email
    )


# Gift (Recipient)
def send_gift_notification_to_recipient(recipient_email, sender_name, gift_message):
    send_user_email(
        subject="You've received a gift from Hobby Hub!",
        message=f"{sender_name} sent you a box!\n\nGift Message:\n{gift_message}",
        recipient_email=recipient_email
    )


# Address changed
def send_address_change_email(user, change_type="updated"):
    send_user_email(
        subject="Your shipping address was " + change_type,
        message=f"Hi {user.username}, your shipping address was {change_type}.",
        recipient_email=user.email
    )


# Account deleted
def send_account_deletion_email(email):
    send_user_email(
        subject="Account Deleted",
        message="Your Hobby Hub account has been successfully deleted.",
        recipient_email=email
    )


# Subscription started
def send_subscription_confirmation_email(user, plan_name):
    send_user_email(
        subject="Subscription Confirmed",
        message=f"You're now subscribed to the {plan_name} plan. Welcome aboard!",
        recipient_email=user.email
    )


# Failed Payment
def send_payment_failed_email(user):
    send_user_email(
        subject="Payment Failed",
        message=(
            f"Hi {user.username},\n\n"
            "Unfortunately, your recent payment attempt for your subscription failed. "
            "Please update your payment method to avoid interruptions."
        ),
        recipient_email=user.email
    )


# Upcoming renewal
def send_upcoming_renewal_email(user, renewal_date):
    send_user_email(
        subject="Your Hobby Hub renewal is coming up",
        message=(
            f"Hi {user.username},\n\n"
            f"Your subscription is set to renew on {renewal_date.strftime('%B %d, %Y')}. "
            "We'll charge your default payment method on file. No action is needed unless you'd like to make changes."
        ),
        recipient_email=user.email
    )

# Shipping Confirmation
def send_shipping_confirmation_email(user, box=None, tracking_number=None):
    box_name = box.name if box else "Hobby Hub"
    tracking_info = f"\nTracking Number: {tracking_number}" if tracking_number else ""
    send_user_email(
        subject="Your Hobby Hub box has shipped!",
        message=(
            f"Hi {user.username},\n\n"
            f"Your {box_name} box has shipped and is on its way!{tracking_info}\n\n"
            "Thanks for being part of the Hobby Hub community."
        ),
        recipient_email=user.email
    )