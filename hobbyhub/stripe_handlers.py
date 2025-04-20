from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
import stripe

from orders.models import Order, Payment, StripeSubscriptionMeta, ShippingAddress, Box
from hobbyhub.mail import (
    send_gift_notification_to_recipient,
    send_gift_confirmation_to_sender,
    send_order_confirmation_email,
    send_subscription_confirmation_email,
    send_payment_failed_email,
    send_upcoming_renewal_email,
)

def handle_checkout_session_completed(session):
    mode = session.get('mode')
    metadata = session.get('metadata', {})
    user_id = metadata.get('user_id')
    print(f"Checkout session completed — mode: {mode}, user_id: {user_id}")

    if not user_id:
        print("No user ID in session metadata")
        return

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        print(f"❌ User with ID {user_id} not found")
        return

    if mode == 'subscription':
        try:
            sub_id = session.get('subscription')
            subscription = stripe.Subscription.retrieve(sub_id)
            price_id = subscription['items']['data'][0]['price']['id']
            shipping = user.addresses.filter(is_default=True).first()

            StripeSubscriptionMeta.objects.create(
                user=user,
                stripe_subscription_id=sub_id,
                stripe_price_id=price_id,
                shipping_address=shipping,
                is_gift=False,
            )

            send_subscription_confirmation_email(user, plan_name="Subscription Box")
            print(f"Subscription created and email sent for {user.username}")

        except Exception as e:
            print(f"Error handling subscription checkout: {e}")

    elif mode == 'payment':
        try:
            payment_intent_id = session.get('payment_intent')
            if not payment_intent_id:
                print("No payment_intent ID found in session")
                return

            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            shipping_info = payment_intent.shipping

            recipient_email = metadata.get('recipient_email')
            sender_name = metadata.get('sender_name', 'Someone')
            gift_message = metadata.get('gift_message', '')
            amount_total = session.get('amount_total', 0)

            if not shipping_info:
                print("No shipping info in payment intent")
                return

            address = ShippingAddress.objects.filter(
                user=user,
                postcode=shipping_info['address']['postal_code']
            ).first()

            if not address:
                print("No matching address found for this shipping info")
                return

            order = Order.objects.create(
                user=user,
                shipping_address=address,
                box=None,
                stripe_subscription_id=None,
                scheduled_shipping_date=None,
                status='processing'
            )

            Payment.objects.create(
                user=user,
                order=order,
                payment_date=timezone.now(),
                amount=amount_total / 100,
                status='paid',
                payment_method='card',
            )

            if recipient_email:
                send_gift_notification_to_recipient(recipient_email, sender_name, gift_message)
                send_gift_confirmation_to_sender(user, recipient_email)
                print(f"Gift confirmation sent to {recipient_email}")
            else:
                send_order_confirmation_email(user, order.id)
                print(f"Order confirmation sent to {user.email}")

        except Exception as e:
            print(f"Error handling one-off payment: {e}")

    else:
        print(f"Unhandled checkout mode: {mode}")



def handle_invoice_payment_succeeded(invoice):
    subscription_id = invoice.get('subscription')
    customer_id = invoice.get('customer')
    amount_paid = invoice['amount_paid'] / 100
    payment_date = timezone.now()

    try:
        customer = stripe.Customer.retrieve(customer_id)
        user = User.objects.get(email=customer.get('email'))

        sub_meta = StripeSubscriptionMeta.objects.filter(
            user=user, stripe_subscription_id=subscription_id
        ).first()

        shipping = sub_meta.shipping_address if sub_meta else user.addresses.filter(is_default=True).first()

        box = Box.objects.filter(is_archived=False).order_by('-shipping_date').first()

        order = Order.objects.create(
            user=user,
            stripe_subscription_id=subscription_id,
            shipping_address=shipping,
            box=box,
            order_date=payment_date.date(),
            scheduled_shipping_date=box.shipping_date if box else None,
            status='processing',
        )

        Payment.objects.create(
            user=user,
            order=order,
            payment_date=payment_date,
            amount=amount_paid,
            status='succeeded',
            payment_method='card',
        )

    except Exception as e:
        print(f"Invoice payment succeeded error: {e}")


def handle_invoice_payment_failed(invoice):
    try:
        customer = stripe.Customer.retrieve(invoice.get('customer'))
        user = User.objects.get(email=customer.get('email'))
        send_payment_failed_email(user)
    except Exception as e:
        print(f"Invoice payment failed error: {e}")


def handle_invoice_upcoming(invoice):
    next_renewal_ts = invoice.get('next_payment_attempt')
    if not next_renewal_ts:
        print("No next_payment_attempt found.")
        return

    next_renewal = timezone.datetime.fromtimestamp(next_renewal_ts, tz=timezone.utc)

    try:
        customer = stripe.Customer.retrieve(invoice.get('customer'))
        user = User.objects.get(email=customer.get('email'))
        send_upcoming_renewal_email(user, next_renewal)
    except Exception as e:
        print(f"Invoice upcoming email error: {e}")