"""
orders/views.py

Handles order and checkout flows including:
- Gift and one-off purchases
- Stripe subscription plans
- Checkout success/cancel pages
- Order history display
"""
import json
import logging

import stripe
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime
from hobbyhub.mail import send_subscription_cancelled_email
from hobbyhub.utils import (alert, build_shipping_details, get_gift_metadata,
                            get_subscription_duration_display,
                            get_subscription_status,
                            get_user_default_shipping_address)
from users.models import ShippingAddress
from .forms import PreCheckoutForm
from .models import Order, Payment, StripeSubscriptionMeta

# Configure Stripe with secret API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Price IDs from settings
GIFT_PRICE_ID = settings.STRIPE_GIFT_PRICE_ID
ONEOFF_PRICE_ID = settings.STRIPE_ONEOFF_PRICE_ID
STRIPE_MONTHLY_PRICE_ID = settings.STRIPE_MONTHLY_PRICE_ID
STRIPE_3MO_PRICE_ID = settings.STRIPE_3MO_PRICE_ID
STRIPE_6MO_PRICE_ID = settings.STRIPE_6MO_PRICE_ID
STRIPE_12MO_PRICE_ID = settings.STRIPE_12MO_PRICE_ID


PLAN_MAP = {
    "oneoff": ONEOFF_PRICE_ID,
    "monthly": STRIPE_MONTHLY_PRICE_ID,
    "3mo": STRIPE_3MO_PRICE_ID,
    "6mo": STRIPE_6MO_PRICE_ID,
    "12mo": STRIPE_12MO_PRICE_ID,
}

logger = logging.getLogger(__name__)


@login_required
def select_purchase_type(request):
    """
    User selects one of the 5 purchase types (single, sub, etc.).
    'gift' passed as ?gift=true or false.
    """
    # clear cached session to ensure address selection happens
    request.session.pop('checkout_shipping_id', None)
    gift = request.GET.get('gift', 'false').lower() == 'true'
    logger.info(f"{request.user} selected purchase type — gift={gift}")
    return render(request, 'orders/select_purchase_type.html', {'gift': gift})


@login_required
def handle_purchase_type(request, plan):
    """
    Routes user to gift message step or checkout based on selection.
    """
    gift_raw = request.GET.get('gift')
    gift = gift_raw and gift_raw.lower() == 'true'

    price_id = PLAN_MAP.get(plan)
    if not price_id:
        logger.warning(f"Invalid plan selected: {plan}")
        alert(request, "error", "Invalid selection.")
        return redirect('select_purchase_type')

    # Force address selection if not already chosen
    if 'checkout_shipping_id' not in request.session:
        logger.info(f"{request.user} selected plan={plan}, gift={gift}")
        url = reverse('choose_shipping_address', args=[plan])
        gift_param = 'true' if gift else 'false'
        return redirect(f"{url}?gift={gift_param}")

    if gift:
        logger.info(f"{request.user} selected plan={plan}, gift={gift}")
        request.session['is_gift'] = True
        request.session.modified = True
        logger.info(
            "[DEBUG] Session content right after setting is_gift=True: "
            f"{request.session.items()}"
        )
        return redirect('gift_message', plan=plan)
    else:
        request.session['is_gift'] = False
        request.session.modified = True
        logger.info(
            "[DEBUG] Session content right after setting is_gift=False: "
            f"{request.session.items()}"
        )

    logger.info(
        "[SESSION DEBUG] Session data after setting is_gift: "
        f"{request.session.items()}"
    )

    # Proceed to correct flow based on plan + gift flag
    if plan == "oneoff" and not gift:
        return handle_checkout(request, price_id)

    if gift:
        logger.info(f"{request.user} selected plan={plan}, gift={gift}")
        return redirect('gift_message', plan=plan)

    return create_subscription_checkout(request, price_id)


@login_required
def gift_message(request, plan):
    logger.info("[DEBUG] Entered gift_message view")

    # Force the session to save
    request.session.modified = True
    request.session.save()

    shipping_id = request.session.get('checkout_shipping_id')
    if not shipping_id:
        request.session['return_to_gift'] = plan
        alert(
            request,
            "info",
            "Before continuing with your gift,"
            " we need a shipping address on file for you."
        )
        return redirect('choose_shipping_address', plan=plan)

    form = PreCheckoutForm(request.POST or None)
    price_id = PLAN_MAP.get(plan)

    context = {
        'form': form,
        'plan': plan
    }

    # If it's a POST request and form is valid, it will continue with Stripe
    if request.method == 'POST':
        if form.is_valid():
            logger.info("Gift message valid, creating Stripe session")

            try:
                is_subscription = plan != 'oneoff'

                # Get gift metadata AND FORCE IS_GIFT
                gift_metadata = get_gift_metadata(
                    form,
                    request.user.id,
                    address_id=shipping_id
                )

                # Hardcode is_gift to true if the session holds it
                is_gift = request.session.get('is_gift', False)
                gift_metadata['gift'] = 'true' if is_gift else 'false'

                logger.info(
                    "[STRIPE CHECKOUT] Metadata before submission: "
                    f"{gift_metadata}"
                )

                shipping_address = ShippingAddress.objects.get(id=shipping_id)
                checkout_data = {
                    'payment_method_types': ['card'],
                    'mode': 'subscription' if is_subscription else 'payment',
                    'line_items': [{'price': price_id, 'quantity': 1}],
                    'metadata': gift_metadata,
                    'customer': request.user.profile.stripe_customer_id,
                    'success_url': request.build_absolute_uri(
                        '/orders/success/'
                    ),
                    'cancel_url': request.build_absolute_uri(
                        '/orders/cancel/'
                    ),
                }

                if not is_subscription:
                    checkout_data['payment_intent_data'] = {
                        'metadata': gift_metadata,
                        'shipping': build_shipping_details(shipping_address),
                    }

                # Force the session to save again before checkout
                request.session.modified = True
                request.session.save()

                session = stripe.checkout.Session.create(**checkout_data)
                logger.info(f"Stripe session created: {session.url}")
                return redirect(session.url)

            except stripe.error.CardError:
                logger.error("Stripe CardError", exc_info=True)
                alert(request, "error", "Your card was declined.")
            except stripe.error.StripeError:
                logger.error("General Stripe error", exc_info=True)
                alert(
                    request,
                    "error",
                    "There was a problem with the payment service."
                )
        else:
            logger.error(f"Form errors: {form.errors}")
            alert(request, "error", "Please correct the errors in the form.")

    return render(request, 'orders/pre_checkout.html', context)


@login_required
def handle_checkout(request, price_id):
    """
    Handles checkout for non-gift one-off purchases.
    Goes straight to Stripe without showing a form.
    """
    logger.info(
        "[DEBUG] Session content at handle_checkout entry: "
        f"{request.session.items()}"
    )
    logger.info(f"{request.user} proceeding to checkout for one-off order")

    shipping_address, redirect_response = get_user_default_shipping_address(
        request
    )
    if redirect_response:
        return redirect_response

    shipping_id = (
        shipping_address.id if shipping_address else None
    )

    metadata = {
        'user_id': request.user.id,
        'shipping_address_id': shipping_id,
        'gift': 'false',
    }

    # Now log after metadata is ready
    logger.info(
        f"[SUBSCRIPTION] Metadata before session creation: {metadata}"
    )
    logger.info(
        f"[SUBSCRIPTION] Session Data: {dict(request.session.items())}"
    )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            metadata={
                'user_id': request.user.id,
                'shipping_address_id': shipping_address.id
            },
            payment_intent_data={
                'metadata': {'user_id': request.user.id},
                'shipping': build_shipping_details(shipping_address),
            },
            customer_email=request.user.email,
            success_url=request.build_absolute_uri('/orders/success/'),
            cancel_url=request.build_absolute_uri('/orders/cancel/'),
        )
        return redirect(session.url, code=303)
    except stripe.error.StripeError:
        logger.error("Stripe error during one-off checkout", exc_info=True)
        alert(
            request,
            "error",
            "There was a problem connecting to the payment service."
            "Please try again shortly."
        )
        return redirect('select_purchase_type')


@login_required
def create_subscription_checkout(request, price_id):
    """
    Handles Stripe checkout session creation for subscription purchases.
    """
    logger.info(f"{request.user} creating subscription session")

    # Get shipping ID from session
    shipping_id = request.session.get('checkout_shipping_id')
    if not shipping_id:
        plan = request.session.get('plan')
        if not plan:
            logger.warning(
                f"Plan not found in session for user {request.user}."
            )
            alert(request, "error", "Please select a valid subscription plan.")
            return redirect('select_purchase_type')

        logger.warning(
            f"No shipping address selected for subscription plan '{plan}'."
        )
        alert(request, "error", "Please select a shipping address.")
        return redirect('choose_shipping_address', plan=plan)

    # Step 1: Determine if it's a gift
    is_gift = request.GET.get('gift', 'false').lower() == 'true'

    # Store it in the session (same as one-off logic)
    if is_gift:
        request.session['is_gift'] = True
    else:
        request.session['is_gift'] = False
    request.session.modified = True
    logger.info(
        f"[SESSION DEBUG] Subscription session — is_gift set to {is_gift}"
    )

    # Step 2: Collect gift details if it's a gift
    if is_gift:
        recipient_name = request.POST.get('recipient_name', '')
        recipient_email = request.POST.get('recipient_email', '')
        sender_name = request.POST.get('sender_name', '')
        gift_message = request.POST.get('gift_message', '')
    else:
        recipient_name = recipient_email = sender_name = gift_message = ''

    # Step 3: Build metadata
    metadata = {
        'user_id': request.user.id,
        'shipping_address_id': shipping_id,
        'gift': 'true' if is_gift else 'false',
        'recipient_name': recipient_name,
        'recipient_email': recipient_email,
        'sender_name': sender_name,
        'gift_message': gift_message
    }

    # Add debug log after metadata is complete
    logger.info(
        f"[DEBUG] Subscription session creation — is_gift={is_gift}, "
        f"metadata={metadata}"
    )

    try:
        address = ShippingAddress.objects.get(id=shipping_id)

        if not address:
            logger.error(f"No address found for ID {shipping_id}")
            alert(request, "error", "Shipping address not found.")
            return redirect('choose_shipping_address')
        else:
            logger.info(f"Found Address: {address}")

        # Step 1: Refresh the user profile before checking the Stripe ID
        request.user.profile.refresh_from_db()

        # Step 2: Now proceed with the ID check
        if not request.user.profile.stripe_customer_id:
            logger.warning(
                """Stripe Customer ID not found in profile.
            Fetching from Stripe..."""
            )
            existing_customers = stripe.Customer.list(
                email=request.user.email,
                limit=1
            )
            if existing_customers.data:
                customer = existing_customers.data[0]
                request.user.profile.stripe_customer_id = customer.id
                request.user.profile.save()
                logger.info(f"Linked existing Stripe Customer: {customer.id}")
            else:
                # If no customer found, create one
                logger.info("No existing customer found, creating a new one.")
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.get_full_name(),
                    metadata={
                        'user_id': request.user.id
                    }
                )
                request.user.profile.stripe_customer_id = customer.id
                request.user.profile.save()
        else:
            # If the ID already exists, fetch it
            customer = stripe.Customer.retrieve(
                request.user.profile.stripe_customer_id
            )
            logger.info(f"Using existing Stripe Customer ID: {customer.id}")

        # Proceed with checkout
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            metadata=metadata,
            success_url=request.build_absolute_uri(
                '/orders/success/?sub=monthly'
            ),
            cancel_url=request.build_absolute_uri('/orders/cancel/'),
        )

        return redirect(checkout_session.url, code=303)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscription creation: {str(e)}")
        alert(
            request,
            "error",
            "There was a problem connecting to the payment service. "
            "Please try again shortly."
        )
        return redirect('subscribe_options')


def order_success(request):
    """
    Renders the order success page with a success message.
    """
    # clear cached session to ensure address selection happens
    request.session.pop('checkout_shipping_id', None)
    logger.info(f"{request.user} reached success page — session cleared")
    alert(
        request,
        "success",
        "Your order was successfully processed. Thank you!"
    )
    return render(request, 'orders/order_success.html')


def order_cancel(request):
    """
    Renders the order cancellation page with an info message.
    """
    # clear cached session to ensure address selection happens
    request.session.pop('checkout_shipping_id', None)
    logger.info(f"{request.user} cancelled checkout — session cleared")
    alert(
        request,
        "info",
        "Your checkout was cancelled, no payment has been taken"
    )
    return render(request, 'orders/order_cancel.html')


@login_required
def order_history(request):
    all_orders = list(Order.objects.select_related("shipping_address").filter(
        user=request.user
    ).order_by('-order_date', '-id'))

    payments = Payment.objects.filter(order__in=all_orders)
    subscriptions = StripeSubscriptionMeta.objects.filter(user=request.user)

    sub_map = {}

    for sub in subscriptions:
        try:
            stripe_subscription = stripe.Subscription.retrieve(
                sub.stripe_subscription_id,
                expand=["latest_invoice"]
            )

            logger.info(
                "[SUBSCRIPTION DEBUG] Full Stripe subscription object: "
                f"{stripe_subscription}")

            # Attempt to retrieve `current_period_end`
            current_period_end = None

            # First, try to get it from the subscription items
            if "items" in stripe_subscription and len(
                stripe_subscription["items"]["data"]
            ) > 0:
                current_period_end = (
                    stripe_subscription["items"]["data"][0]
                    .get("current_period_end")
                )

            # If it wasn't found, fallback to `billing_cycle_anchor`
            if not current_period_end:
                current_period_end = stripe_subscription.get(
                    "billing_cycle_anchor"
                )

            if current_period_end:
                current_period_end = datetime.fromtimestamp(current_period_end)
                logger.info(
                    "[SUBSCRIPTION DEBUG] Found current_period_end for "
                    f"{sub.stripe_subscription_id}: {current_period_end}"
                )
            else:
                current_period_end = "Not Available"
                logger.warning(
                    "[SUBSCRIPTION DEBUG] No current_period_end found for "
                    f"{sub.stripe_subscription_id}"
                )

            # Populate the sub_map with additional data
            sub_map[sub.stripe_subscription_id] = {
                'sub': sub,
                'label': get_subscription_duration_display(sub),
                'status': get_subscription_status(sub),
                'is_gift': sub.is_gift,
                'current_period_end': current_period_end
            }

        except Exception as e:
            logger.error(
                "Failed to retrieve subscription "
                f"{sub.stripe_subscription_id}: {e}"
            )
            sub_map[sub.stripe_subscription_id] = {
                'sub': sub,
                'label': get_subscription_duration_display(sub),
                'status': get_subscription_status(sub),
                'is_gift': sub.is_gift,
                'current_period_end': None  # Set to None if fetch fails
            }

    payments_by_order = {p.order_id: p for p in payments}

    sub_orders = [o for o in all_orders if o.stripe_subscription_id]
    oneoff_orders = [o for o in all_orders if not o.stripe_subscription_id]

    return render(request, 'orders/order_history.html', {
        'subscriptions': sub_orders,
        'orders': oneoff_orders,
        'payments_by_order': payments_by_order,
        'get_subscription_duration_display': get_subscription_duration_display,
        'sub_map': sub_map,
    })


@require_POST
@login_required
@csrf_exempt
def secure_cancel_subscription(request):
    """
    Cancels the user's subscription securely after password confirmation.
    """
    data = json.loads(request.body)
    password = data.get('password')
    subscription_id = data.get('subscription_id')

    if not subscription_id:
        logger.error(
            "Cancel subscription request with no subscription ID from user "
            f"{request.user}"
        )
        return JsonResponse({
            'success': False,
            'error': 'Subscription ID not provided.'
        })

    if authenticate(username=request.user.username, password=password):
        try:
            sub = StripeSubscriptionMeta.objects.get(
                user=request.user,
                stripe_subscription_id=subscription_id,
                cancelled_at__isnull=True
            )

            stripe.Subscription.modify(
                sub.stripe_subscription_id,
                cancel_at_period_end=True
            )

            sub.cancelled_at = timezone.now()
            sub.save()

            send_subscription_cancelled_email(
                request.user,
                plan_id=sub.stripe_price_id,
                start_date=sub.created_at
            )

            logger.info(
                f"Subscription {subscription_id} cancelled "
                f"for user {request.user}"
            )
            return JsonResponse({
                'success': True,
                'message': 'Subscription will cancel at period end.'
            })

        except StripeSubscriptionMeta.DoesNotExist:
            logger.warning(
                f"{request.user} "
                f"tried to cancel {subscription_id} "
                "but no active subscription found"
            )
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found to cancel.'
            })

    else:
        return JsonResponse({
            'success': False,
            'error': 'Incorrect password'
        })


@login_required
def choose_shipping_address(request, plan):
    """
    Lets the user select a shipping address before checkout.
    Filters based on gift/self.
    Stores selected address in session and redirects accordingly.
    """
    gift = request.GET.get('gift', 'false').lower() == 'true'
    logger.debug(f"gift={gift} in choose_shipping_address")

    # Filter addresses based on gift flag
    addresses = request.user.addresses.filter(is_gift_address=gift)

    if request.method == 'POST':
        selected_id = request.POST.get('shipping_address')
        if not selected_id:
            logger.warning(
                f"{request.user} "
                f"submitted without selecting a shipping address"
            )
            alert(request, "error", "Please select an address.")
            return redirect('choose_shipping_address', plan=plan)

        if not request.user.addresses.filter(id=selected_id).exists():
            logger.warning(
                f"Address ID {selected_id} not found for user {request.user}"
            )
            alert(request, "error", "Invalid address selected.")
            return redirect('choose_shipping_address', plan=plan)

        logger.info(
            f"{request.user} selected shipping address ID "
            f"{selected_id} for plan {plan}, gift={gift}"
        )
        request.session['checkout_shipping_id'] = int(selected_id)

        if gift:
            request.session['is_gift'] = True
        else:
            request.session['is_gift'] = False
        request.session.modified = True

        logger.info(
            "[SESSION DEBUG] After address selection, session data: "
            f"{request.session.items()}"
        )

        if gift:
            return redirect('gift_message', plan=plan)
        if plan == "oneoff":
            return redirect('handle_purchase_type', plan='oneoff')

        logger.debug(f"Plan is: {plan}")
        logger.debug(f"Session data: {request.session.items()}")
        logger.debug(f"Next redirect: /orders/purchase/{plan}/")

        return redirect(f'/orders/purchase/{plan}/')

    if gift:
        back_url = reverse('select_purchase_type') + '?gift=true'
    else:
        back_url = reverse('select_purchase_type') + '?gift=false'

    return render(request, 'orders/choose_shipping_address.html', {
        'addresses': addresses,
        'plan': plan,
        'gift': gift,
        'back_url': back_url,
    })
