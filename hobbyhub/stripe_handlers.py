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
import logging
import time

import stripe
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone

from hobbyhub.mail import (
    send_gift_confirmation_to_sender,
    send_gift_notification_to_recipient,
    send_order_confirmation_email,
    send_payment_failed_email,
    send_subscription_confirmation_email,
    send_upcoming_renewal_email
)
from hobbyhub.utils import PLAN_MAP
from orders.models import (Box, Order, Payment, ShippingAddress,
                           StripeSubscriptionMeta)

logger = logging.getLogger(__name__)


def handle_checkout_session_completed(session):
    """
    Handle Stripe Checkout session completion.
    """
    mode = session.get('mode')
    metadata = session.get('metadata', {})
    user_id = metadata.get('user_id')
    address_id = metadata.get('shipping_address_id')

    # 🔍 Check the explicit gift flag
    gift_flag = metadata.get('gift', 'false').lower() == 'true'
    is_gift = gift_flag
    logger.info(
        f"[WEBHOOK] Gift parsing logic — gift flag from metadata: {gift_flag}"
    )

    recipient_email = metadata.get('recipient_email', '')
    sender_name = metadata.get('sender_name', '')
    recipient_name = metadata.get('recipient_name', '')

    if not user_id or not address_id:
        logger.error("User ID or Address ID missing from metadata.")
        return

    logger.info(
        f"[WEBHOOK] Gift parsing logic — recipient_email: {recipient_email}, "
        f"sender_name: {sender_name}, recipient_name: {recipient_name}, "
        f"parsed is_gift: {is_gift}"
    )

    logger.info(
        f"[WEBHOOK] Gift parsing logic — recipient_email: {recipient_email}, "
        f"parsed is_gift: {is_gift}"
    )

    logger.info(f"[WEBHOOK] Metadata received from Stripe: {metadata}")
    logger.info(
        f"[WEBHOOK] Subscription ID received: {session.get('subscription')}"
    )
    logger.info(
        f"[WEBHOOK] Mode: {mode}, User ID: {user_id}, Address ID: {address_id}"
    )
    logger.info(f"[WEBHOOK] Metadata received: {metadata}")
    logger.info(f"[WEBHOOK] Parsed is_gift: {is_gift}")
    logger.info(f"[WEBHOOK] Subscription ID: {session.get('subscription')}")
    logger.info(
        f"Checkout session completed — mode: {mode}, "
        f"user_id: {user_id}, address_id: {address_id}"
    )

    if not user_id:
        logger.error("No user ID in session metadata")
        return

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return

    box = (
        Box.objects.filter(is_archived=False)
                   .order_by('-shipping_date')
                   .first()
    )

    if not box:
        logger.error(
            "[CRITICAL] No active boxes found for Order creation."
            "Retrying in 2 seconds."
        )
        time.sleep(2)
        box = (
            Box.objects.filter(
                is_archived=False
            ).order_by(
                '-shipping_date'
            ).first()
        )
        if not box:
            logger.critical(
                "[CRITICAL] Retry failed."
                "No active boxes available."
                "This order will be missing a Box ID and Shipping Date."
            )

    if mode == 'subscription':
        try:
            session = (
                stripe.checkout.Session.retrieve(
                    session["id"],
                    expand=["subscription"]
                )
            )
            sub = session.subscription
            if not sub:
                logger.error("No subscription found in expanded session")
                return

            sub_id = sub.id
            price_id = sub["items"]["data"][0]["price"]["id"]

            # ADDITIONAL LOGGING HERE
            logger.info(
                f"Retrieved subscription: {sub_id},"
                f"price_id: {price_id}"
            )

            # Create Subscription Meta
            try:
                shipping_address = (
                    ShippingAddress.objects.get(id=address_id, user=user)
                )
                logger.info(f"Fetched Shipping Address: {shipping_address}")
                logger.info(f"Address ID: {address_id} | User: {user}")
            except ShippingAddress.DoesNotExist:
                logger.error(
                    f"No address found for user {user.id} "
                    f"with address_id={address_id}"
                )
                return

            with transaction.atomic():
                # Lock the row to prevent race conditions
                existing_subs = (
                    StripeSubscriptionMeta.objects.select_for_update()
                    .filter(stripe_subscription_id=sub_id)
                )
                
                if existing_subs.exists():
                    sub_meta = existing_subs.first()
                    created = False
                    logger.warning(
                        f"[SKIP] StripeSubscriptionMeta for {sub_id} "
                        "already exists"
                    )
                else:
                    sub_meta = StripeSubscriptionMeta.objects.create(
                        stripe_subscription_id=sub_id,
                        is_gift=is_gift,
                        shipping_address_id=address_id,
                        user_id=user_id
                    )
                    created = True
                    logger.info(
                        f"[CREATED] StripeSubscriptionMeta for {sub_id}"
                    )

            # Extract directly from metadata for email only
            recipient_email = metadata.get('recipient_email')
            recipient_name = metadata.get('recipient_name', 'Friend')
            sender_name = metadata.get('sender_name', 'Someone')
            gift_message = metadata.get('gift_message', '')

            # Send the appropriate emails
            if is_gift and recipient_email:
                send_gift_notification_to_recipient(
                    recipient_email,
                    sender_name,
                    gift_message,
                    recipient_name
                )
                send_gift_confirmation_to_sender(user, recipient_name)
                logger.info(
                    f"[EMAIL] Gift confirmation sent to {recipient_email}"
                )
            else:
                _, plan_name = PLAN_MAP.get(price_id, (None, "Unknown Plan"))
                send_subscription_confirmation_email(user, plan_name)
                logger.info(
                    "[EMAIL] Subscription confirmation email "
                    f"sent to {user.email} for {plan_name}"
                )

                if created:
                    logger.info(
                        f"[CREATED] StripeSubscriptionMeta for {sub_id} "
                        f"with is_gift={is_gift}"
                    )
                else:
                    logger.warning(
                        f"[EXISTS] StripeSubscriptionMeta for {sub_id} "
                        "already exists, skipping creation."
                    )

            if not created:
                sub_meta.stripe_price_id = price_id
                sub_meta.shipping_address = shipping_address
                sub_meta.is_gift = is_gift
                sub_meta.save()

            logger.info(
                f"[CREATED] StripeSubscriptionMeta for {sub_id} "
                f"with is_gift={is_gift}"
            )
            logger.info(f"Created StripeSubscriptionMeta for {sub_id}")

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
                    logger.info(
                        f"[EMAIL] Gift confirmation sent to {recipient_email}"
                    )
                else:
                    send_subscription_confirmation_email(user, plan_name)
                    logger.info(
                        "[EMAIL] Subscription confirmation email "
                        f"sent to {user.email} "
                        f"for {plan_name}"
                    )
            except Exception as e:
                logger.error(f"Error in creating subscription/order: {e}")
                raise

        except Exception as e:
            logger.error(f"Error in creating subscription/order: {e}")

    elif mode == 'payment':
        try:
            # Fetch the payment_intent_id
            payment_intent_id = session.get('payment_intent')
            if not payment_intent_id:
                logger.error(
                    "No payment_intent_id "
                    f"found for session {session.get('id')}"
                )
                return

            # Check if the payment already exists
            if Payment.objects.filter(
                payment_intent_id=payment_intent_id
            ).exists():
                logger.info(
                    f"[SKIP] PaymentIntent {payment_intent_id} "
                    "already processed, skipping."
                )
                return

            # Retrieve the PaymentIntent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            shipping_info = payment_intent.shipping

            # Validate shipping info
            if not shipping_info or not shipping_info.address:
                logger.error(
                    "No shipping info found in "
                    f"PaymentIntent {payment_intent_id}"
                )
                return

            # Attempt to get the Shipping Address from DB
            try:
                shipping_address = (
                    ShippingAddress.objects.get(
                        id=address_id,
                        user=user
                    )
                )
            except ShippingAddress.DoesNotExist:
                logger.error(
                    f"No address found for user {user.id} "
                    f"with address_id={address_id}"
                )
                return

            # Extract metadata directly
            recipient_email = metadata.get('recipient_email')
            recipient_name = metadata.get('recipient_name', 'Friend')
            sender_name = metadata.get('sender_name', 'Someone')
            gift_message = metadata.get('gift_message', '')

            # Transaction-safe creation of Order and Payment
            with transaction.atomic():
                order, created = Order.objects.get_or_create(
                    stripe_payment_intent_id=payment_intent_id,
                    defaults={
                        'user': user,
                        'shipping_address': shipping_address,
                        'box': box,
                        'order_date': timezone.now().date(),
                        'scheduled_shipping_date': (
                            box.shipping_date if box else None
                        ),
                        'status': 'processing',
                        'is_gift': is_gift
                    }
                )

                # Always refresh from DB, even if it wasn't created
                order.refresh_from_db()
                logger.info(
                    f"[POST-REFRESH] Order {order.id}. Box ID: {order.box_id},"
                    f"Scheduled Shipping Date: {order.scheduled_shipping_date}"
                )

                if not order.box_id:
                    logger.warning(
                        f"[DB WARNING] Order {order.id} "
                        f"was created without a Box ID. Expected Box ID: "
                        f"{box.id if box else 'None'}"
                    )

                if created:
                    logger.info(
                        f"[CREATED] Order {order.id} for payment intent "
                        f"{payment_intent_id} with is_gift={is_gift}"
                    )
                else:
                    if is_gift and not order.is_gift:
                        logger.warning(
                            f"[FORCE UPDATE] Order {order.id} -> is_gift=True"
                        )
                        order.is_gift = True
                        order.save(update_fields=['is_gift'])
                        order.refresh_from_db()
                        if not order.is_gift:
                            logger.error(
                                f"[DB MISMATCH] Order {order.id} "
                                "still reports is_gift=False after save."
                            )
                        else:
                            logger.info(
                                f"[DB SUCCESS] Order {order.id} "
                                "is_gift=True now reflected in DB"
                            )

            # Create Payment Record
            if not Payment.objects.filter(
                payment_intent_id=payment_intent_id
            ).exists():
                Payment.objects.create(
                    user=user,
                    order=order,
                    payment_date=timezone.now(),
                    amount=payment_intent.amount_received / 100,
                    status='paid',
                    payment_method='card',
                    payment_intent_id=payment_intent_id,
                )
                logger.info(
                    f"[CREATED] One-off order ID {order.id} "
                    f"and payment {payment_intent_id} for user {user.id}"
                )
            else:
                logger.warning(
                    f"[SKIP] PaymentIntent {payment_intent_id} "
                    "already processed, skipping payment creation."
                )

            # Send the appropriate emails
            if is_gift:
                if recipient_email and recipient_name:
                    # Send recipient and sender notifications
                    send_gift_notification_to_recipient(
                        recipient_email,
                        sender_name or "Someone",
                        gift_message or "No message provided.",
                        recipient_name
                    )
                    send_gift_confirmation_to_sender(user, recipient_name)
                    logger.info(
                        f"[EMAIL] Gift confirmation sent to {recipient_email}"
                    )
                else:
                    # 🚨 **Graceful logging for incomplete data**
                    logger.warning(
                        "[EMAIL WARNING] Gift selected but recipient "
                        "information is incomplete: "
                        f"Email='{recipient_email}', Name='{recipient_name}'"
                    )

        except Exception as e:
            logger.error(f"Error handling one-off payment: {e}")

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
        email = customer.get('email')
        if not email:
            logger.error(
                f"No email found for Stripe customer {customer.id} "
                f"for invoice {invoice.get('id')}"
            )
            return

        user = User.objects.get(email=email)

        # Fetch associated subscription metadata
        sub_meta, created = StripeSubscriptionMeta.objects.get_or_create(
            stripe_subscription_id=subscription_id,
            defaults={
                'user': user,
                'stripe_price_id': invoice['lines']['data'][0]['price']['id'],
                'shipping_address': None,  # Update when available
                'is_gift': False
            }
        )

        shipping_address = sub_meta.shipping_address
        if not shipping_address:
            logger.warning(
                f"[MISSING ADDRESS] Sub ID: {subscription_id} "
                f"has no associated shipping address. Checking DB now."
            )
            
            # Attempt to fetch from DB
            address = ShippingAddress.objects.filter(user=user).first()
            if address:
                sub_meta.shipping_address = address
                sub_meta.save()
                shipping_address = address  # Assign it to continue with logic
                logger.info(
                    f"[RECOVERED] Assigned address {address.id} to subscription {subscription_id}"
                )
            else:
                logger.error(f"[FAILED RECOVERY] No address found for user {user.id}")
                return


        if not created:
            # Sync the data if it already existed
            sub_meta.stripe_price_id = (
                invoice['lines']['data'][0]['price']['id']
            )
            sub_meta.shipping_address = shipping_address
            sub_meta.is_gift = sub_meta.is_gift
            sub_meta.save()

        shipping = sub_meta.shipping_address
        if not shipping:
            logger.error(
                f"Subscription {subscription_id} has no shipping address"
            )
            return

        # Find the latest box
        box = (
            Box.objects.filter(is_archived=False)
            .order_by('-shipping_date')
            .first()
        )

        # Fetch or create the order
        try:
            order, created = Order.objects.get_or_create(
                stripe_subscription_id=subscription_id,
                defaults={
                    'user': user,
                    'shipping_address': shipping_address,
                    'box': box,
                    'order_date': payment_date.date(),
                    'scheduled_shipping_date': (
                        box.shipping_date if box else None
                    ),
                    'status': 'processing',
                    'is_gift': sub_meta.is_gift
                }
            )
            if created:
                logger.info(
                    f"[CREATED] Order {order.id} "
                    f"for subscription {subscription_id} "
                    f"with is_gift={sub_meta.is_gift}"
                )
            else:
                logger.warning(
                    f"[EXISTS] Order {order.id} already exists "
                    f"for subscription {subscription_id}"
                )
                if sub_meta.is_gift and not order.is_gift:
                    logger.warning(f"[FORCE UPDATE] Order {order.id} -> is_gift=True")
                    order.is_gift = True
                    order.save(update_fields=['is_gift'])
                    order.refresh_from_db()
                    if not order.is_gift:
                        logger.error(f"[DB MISMATCH] Order {order.id} still reports is_gift=False after save.")
                    else:
                        logger.info(f"[DB SUCCESS] Order {order.id} is_gift=True now reflected in DB")
        except Exception as e:
            logger.error(
                "Failed to create Order for subscription %s: %s",
                subscription_id,
                e
            )


        if not invoice.get('payment_intent'):
            logger.error(
                f"No payment_intent found for invoice {invoice.get('id')}"
            )
            return

        # Always create a Payment record
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
            logger.info(
                f"[EMAIL] Sent confirmation email for Order {order.id} "
                f"to {user.email}"
            )
        else:
            logger.warning(
                f"[EXISTS] Payment already exists for Order {order.id}"
            )

    except IntegrityError:
        logger.warning(
            f"Duplicate Order creation blocked for sub ID {subscription_id}"
        )
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
        logger.error(
            "No next_payment_attempt found. "
            "Cannot proceed with invoice renewal."
        )
        return

    try:
        next_renewal = timezone.datetime.fromtimestamp(
            next_renewal_ts,
            tz=timezone.utc
        )
    except (ValueError, TypeError):
        logger.error(
            f"Invalid timestamp for renewal on invoice {invoice.get('id')}: "
            f"{next_renewal_ts}"
        )
        return

    try:
        customer = stripe.Customer.retrieve(invoice.get('customer'))
        user = User.objects.get(email=customer.get('email'))
        send_upcoming_renewal_email(user, next_renewal)
    except Exception as e:
        logger.error(f"Invoice upcoming email error: {e}")
