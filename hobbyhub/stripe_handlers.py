"""
stripe_handlers.py

Handles Stripe webhook events and checkout session completions.

Main responsibilities:
- Create subscriptions and orders based on Stripe session data.
- Handle invoice payment successes, failures, and upcoming renewals.
- Send appropriate confirmation or failure emails to users.
- Sync Stripe customer and subscription data with local database models.

Relies on:
- Stripe API
- Django ORM (orders, users, subscriptions)
- HobbyHub custom mailers
"""
import stripe
import logging
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

from orders.models import (
    Order,
    Payment,
    StripeSubscriptionMeta,
    ShippingAddress,
    Box
)
from hobbyhub.mail import (
    send_gift_notification_to_recipient,
    send_gift_confirmation_to_sender,
    send_order_confirmation_email,
    send_subscription_confirmation_email,
    send_payment_failed_email,
    send_upcoming_renewal_email,
)
from hobbyhub.utils import PLAN_MAP


logger = logging.getLogger(__name__)


def handle_checkout_session_completed(session):
    """
    Handle Stripe Checkout session completion.
    """
    mode = session.get('mode')
    metadata = session.get('metadata', {})
    user_id = metadata.get('user_id')
    address_id = metadata.get('shipping_address_id')

    # Explicitly force it to Boolean
    is_gift = bool(metadata.get('recipient_email'))
    logger.info(f"[WEBHOOK] Parsed is_gift as: {is_gift}")



    logger.info(f"[WEBHOOK] Metadata received from Stripe: {metadata}")
    logger.info(f"[WEBHOOK] Subscription ID received: {session.get('subscription')}")
    logger.info(f"[WEBHOOK] Mode: {mode}, User ID: {user_id}, Address ID: {address_id}")
    logger.info(f"[WEBHOOK] Metadata received: {metadata}")
    logger.info(f"[WEBHOOK] Parsed is_gift: {is_gift}")
    logger.info(f"[WEBHOOK] Subscription ID: {session.get('subscription')}")
    logger.info(f"Checkout session completed — mode: {mode}, user_id: {user_id}, address_id: {address_id}")

    if not user_id:
        logger.error("No user ID in session metadata")
        return

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return

    if mode == 'subscription':
        try:
            session = stripe.checkout.Session.retrieve(session["id"], expand=["subscription"])
            sub = session.subscription
            if not sub:
                logger.error("No subscription found in expanded session")
                return

            sub_id = sub.id
            price_id = sub["items"]["data"][0]["price"]["id"]

            # ADDITIONAL LOGGING HERE
            logger.info(f"Retrieved subscription: {sub_id}, price_id: {price_id}")
            
            # Create Subscription Meta
            StripeSubscriptionMeta.objects.create(
                user=user,
                stripe_subscription_id=sub_id,
                stripe_price_id=price_id,
                shipping_address_id=address_id,
                is_gift=is_gift
            )
            logger.info(f"[CREATED] StripeSubscriptionMeta for {sub_id} with is_gift={is_gift}")
            logger.info(f"Created StripeSubscriptionMeta for {sub_id}")

            # Create Order
            box = Box.objects.filter(is_archived=False).order_by('-shipping_date').first()
            Order.objects.create(
                user=user,
                stripe_subscription_id=sub_id,
                shipping_address_id=address_id,
                box=box,
                order_date=timezone.now().date(),
                scheduled_shipping_date=box.shipping_date if box else None,
                status='processing',
                is_gift=is_gift
            )
            logger.info(f"[CREATED] Order for subscription {sub_id} with is_gift={is_gift}")

            try:
                _, plan_name = PLAN_MAP.get(price_id, (None, "Unknown Plan"))
                
                if is_gift and metadata.get('recipient_email'):
                    recipient_email = metadata['recipient_email']
                    recipient_name = metadata.get('recipient_name', 'Friend')
                    sender_name = metadata.get('sender_name', 'Someone')
                    gift_message = metadata.get('gift_message', '')

                    send_gift_notification_to_recipient(
                        recipient_email,
                        sender_name,
                        gift_message,
                        recipient_name
                    )
                    send_gift_confirmation_to_sender(user, recipient_name)
                    logger.info(f"[EMAIL] Gift confirmation sent to {recipient_email}")
                else:
                    send_subscription_confirmation_email(user, plan_name)
                    logger.info(f"[EMAIL] Subscription confirmation email sent to {user.email} for {plan_name}")
            except Exception as e:
                logger.error(f"Error in creating subscription/order: {e}")


        except Exception as e:
            logger.error(f"Error in creating subscription/order: {e}")


    elif mode == 'payment':
        try:
            if 'payment_intent' not in session or not session['payment_intent']:
                session = stripe.checkout.Session.retrieve(
                    session["id"],
                    expand=["payment_intent"]
                )

            print("Stripe Session Object: ", session)
            # Get the payment intent ID from the session
            payment_intent_id = session['payment_intent']

            if Payment.objects.filter(payment_intent_id=payment_intent_id).exists():
                logger.warning(f"[SKIP] PaymentIntent {payment_intent_id} already handled, skipping.")
                return

            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            shipping_info = payment_intent.shipping

            if not shipping_info:
                logger.info("No shipping info in payment intent")
                return
            
            address_id = metadata.get('shipping_address_id')
            address = ShippingAddress.objects.filter(user=user, id=address_id).first()

            # If the ID lookup fails, fallback to postcode
            if not address:
                postcode = shipping_info['address']['postal_code']
                address = ShippingAddress.objects.filter(
                    user=user,
                    postcode__iexact=postcode  # <-- Case-insensitive search
                ).first()

            recipient_email = metadata.get('recipient_email')
            sender_name = metadata.get('sender_name', 'Someone')
            gift_message = metadata.get('gift_message', '')
            amount_total = session.get('amount_total', 0)

            try:
                with transaction.atomic():
                    order = Order.objects.select_for_update().filter(stripe_payment_intent_id=payment_intent_id).first()
                    if order:
                        logger.warning(f"[SKIP] PaymentIntent {payment_intent_id} already exists.")
                        return

                    # If no order exists, we create it
                    order = Order.objects.create(
                        user=user,
                        shipping_address=address,
                        box=None,
                        stripe_subscription_id=None,
                        stripe_payment_intent_id=payment_intent_id,
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
                        payment_intent_id=payment_intent.id,
                    )
                    logger.warning(f"[CREATED] One-off order ID {order.id} and payment {payment_intent.id} for user {user.id}")

            except IntegrityError as e:
                logger.error(f"IntegrityError detected: {e}")


            logger.warning(f"[CREATED] One-off order ID {order.id} and payment {payment_intent.id} for user {user.id}")

            if is_gift and recipient_email:
                recipient_name = metadata.get('recipient_name', 'Friend')
                send_gift_notification_to_recipient(
                    recipient_email,
                    sender_name,
                    gift_message,
                    recipient_name
                )
                send_gift_confirmation_to_sender(user, recipient_name)
                logger.info(f"Gift confirmation sent to {recipient_email}")
            else:
                send_order_confirmation_email(user, order.id)
                logger.info(f"Order confirmation sent to {user.email}")


        except Exception as e:
            logger.error(f"Error handling one-off payment: {e}")

    else:
        logger.error(f"Unhandled checkout mode: {mode}")


def handle_invoice_payment_succeeded(invoice):
    """
    Handle successful Stripe subscription invoice payment.

    Args:
        invoice (dict): The Stripe invoice object.

    - Creates a new Order and Payment record.
    - Links orders to the latest available Box if one exists.
    - Logs success or error.
    """
    subscription_id = invoice.get('subscription')
    customer_id = invoice.get('customer')
    amount_paid = invoice['amount_paid'] / 100
    payment_date = timezone.now()

    try:
        # Fetch the customer from Stripe
        customer = stripe.Customer.retrieve(customer_id)
        user = User.objects.get(email=customer.get('email'))

        # Fetch associated subscription metadata
        sub_meta = StripeSubscriptionMeta.objects.filter(
            stripe_subscription_id=subscription_id
        ).select_related('shipping_address').first()

        if not sub_meta:
            logger.error(f"No StripeSubscriptionMeta found for sub ID {subscription_id}")
            return

        shipping = sub_meta.shipping_address
        if not shipping:
            logger.error(f"Subscription {subscription_id} has no shipping address")
            return

        # Find the latest box
        box = (
            Box.objects.filter(is_archived=False)
            .order_by('-shipping_date')
            .first()
        )

        # ➡️ Fetch or create the order
        order, created = Order.objects.get_or_create(
            stripe_subscription_id=subscription_id,
            defaults={
                'user': user,
                'shipping_address': shipping,
                'box': box,
                'order_date': payment_date.date(),
                'scheduled_shipping_date': box.shipping_date if box else None,
                'status': 'processing',
                'is_gift': sub_meta.is_gift   # <-- Ensure it is stored here
            }
        )

        if created:
            logger.info(f"[CREATED] Order {order.id} for subscription {subscription_id} with is_gift={sub_meta.is_gift}")
        else:
            logger.warning(f"[EXISTS] Order {order.id} already exists for subscription {subscription_id}")

        # ➡️ Always create a Payment record
        payment, created = Payment.objects.get_or_create(
            payment_intent_id=invoice.get('payment_intent'),
            defaults={
                'user': user,
                'order': order,
                'payment_date': payment_date,
                'amount': amount_paid,
                'status': 'succeeded',
                'payment_method': 'card',
            }
        )



        if created:
            logger.info(f"[CREATED] Payment for Order {order.id}")
            # Send the confirmation email
            send_order_confirmation_email(user, order.id)
            logger.info(f"[EMAIL] Sent confirmation email for Order {order.id} to {user.email}")
        else:
            logger.warning(f"[EXISTS] Payment already exists for Order {order.id}")

    except IntegrityError:
        logger.warning(f"Duplicate Order creation blocked for sub ID {subscription_id}")
    except Exception as e:
        logger.error(f"Invoice payment succeeded error: {e}")



def handle_invoice_payment_failed(invoice):
    """
    Handle failed Stripe invoice payment.

    Args:
        invoice (dict): The Stripe invoice object.

    - Sends a payment failure notification email to the user.
    - Logs error if user lookup fails.
    """
    try:
        customer = stripe.Customer.retrieve(invoice.get('customer'))
        user = User.objects.get(email=customer.get('email'))
        send_payment_failed_email(user)
    except Exception as e:
        logger.error(f"Invoice payment failed error: {e}")


def handle_invoice_upcoming(invoice):
    """
    Handle upcoming Stripe invoice renewal.

    Args:
        invoice (dict): The Stripe invoice object.

    - Sends a notification to the user reminding them of the upcoming charge.
    - Only sends if `next_payment_attempt` is available.
    - Logs error if user lookup fails.
    """
    next_renewal_ts = invoice.get('next_payment_attempt')
    if not next_renewal_ts:
        logger.info("No next_payment_attempt found.")
        return

    next_renewal = timezone.datetime.fromtimestamp(
        next_renewal_ts,
        tz=timezone.utc
    )

    try:
        customer = stripe.Customer.retrieve(invoice.get('customer'))
        user = User.objects.get(email=customer.get('email'))
        send_upcoming_renewal_email(user, next_renewal)
    except Exception as e:
        logger.error(f"Invoice upcoming email error: {e}")
