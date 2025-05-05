"""
orders/views.py

Handles order and checkout flows including:
- Gift and one-off purchases
- Stripe subscription plans
- Checkout success/cancel pages
- Order history display
"""
# Django/External Imports
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
import logging
import stripe
import json


# Local imports
from hobbyhub.utils import (
    alert,
    get_user_default_shipping_address,
    build_shipping_details,
    get_gift_metadata,
    get_subscription_duration_display,
    get_subscription_status
)
from .models import Order, Payment, StripeSubscriptionMeta
from hobbyhub.mail import send_subscription_cancelled_email
from users.models import ShippingAddress
from .forms import PreCheckoutForm

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
def order_start(request):
    """
    Presents user with choice: Buy for self or gift.
    """
    # Force address selection due to session caching
    request.session.pop('checkout_shipping_id', None)
    logger.info(f"{request.user} started an order (fresh session)")
    return render(request, 'orders/order_start.html')


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
        return redirect('order_start')

    # ✅ Force address selection if not already chosen
    if 'checkout_shipping_id' not in request.session:
        logger.info(f"{request.user} selected plan={plan}, gift={gift}")
        url = reverse('choose_shipping_address', args=[plan])
        gift_param = 'true' if gift else 'false'
        return redirect(f"{url}?gift={gift_param}")

    # ⬇️ Proceed to correct flow based on plan + gift flag
    if plan == "oneoff" and not gift:
        return handle_checkout(request, price_id)

    if gift:
        logger.info(f"{request.user} selected plan={plan}, gift={gift}")
        return redirect('gift_message', plan=plan)

    return create_subscription_checkout(request, price_id)


@login_required
def gift_message(request, plan):
    logger.info(f"{request.user} is entering gift message for {plan} plan")

    # Only redirect if shipping ID is not in session
    shipping_id = request.session.get('checkout_shipping_id')
    if not shipping_id:
        request.session['return_to_gift'] = plan
        alert(
            request,
            "info",
            "Before continuing with your gift,"
            " we need a shipping address on file for you."
        )
        return redirect('choose_shipping_address', plan=plan)  # <- Fix here

    form = PreCheckoutForm(request.POST or None)
    price_id = PLAN_MAP.get(plan)

    if request.method == 'POST':
        if form.is_valid():
            logger.info("Gift message valid, creating Stripe session")

            try:
                is_subscription = plan != 'oneoff'

                gift_metadata = get_gift_metadata(
                    form,
                    request.user.id,
                    address_id=shipping_id
                )

                shipping_address = ShippingAddress.objects.get(id=shipping_id)

                checkout_data = {
                    'payment_method_types': ['card'],
                    'mode': 'subscription' if is_subscription else 'payment',
                    'line_items': [{'price': price_id, 'quantity': 1}],
                    'metadata': gift_metadata,
                    'customer_email': request.user.email,
                    'success_url': request.build_absolute_uri('/orders/success/'),
                    'cancel_url': request.build_absolute_uri('/orders/cancel/'),
                }

                if not is_subscription:
                    checkout_data['payment_intent_data'] = {
                        'metadata': gift_metadata,
                        'shipping': build_shipping_details(shipping_address),
                    }

                session = stripe.checkout.Session.create(**checkout_data)
                return redirect(session.url, code=303)

            except stripe.error.CardError:
                logger.error("Stripe CardError", exc_info=True)
                alert(request, "error", "Your card was declined.")

            except stripe.error.StripeError:
                logger.error("General Stripe error", exc_info=True)
                alert(request, "error", "There was a problem with the payment service.")

        else:
            alert(request, "error", "Please correct the errors in the form.")

    return render(request, 'orders/pre_checkout.html', {'form': form})


@login_required
def handle_checkout(request, price_id):
    """
    Handles checkout for non-gift one-off purchases.
    Goes straight to Stripe without showing a form.
    """
    logger.info(f"{request.user} proceeding to checkout for one-off order")
    shipping_address, redirect_response = get_user_default_shipping_address(
        request
    )
    if redirect_response:
        return redirect_response

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            metadata={'user_id': request.user.id},
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
        return redirect('order_start')


@login_required
@login_required
def create_subscription_checkout(request, price_id):
    """
    Handles Stripe checkout session creation for subscription purchases.
    """
    logger.info(f"{request.user} creating subscription session")

    # ✅ Get shipping ID from session
    shipping_id = request.session.get('checkout_shipping_id')
    if not shipping_id:
        logger.warning("No shipping address selected for subscription.")
        alert(request, "error", "Please select a shipping address.")
        return redirect('order_start')

    metadata = {
        'user_id': request.user.id,
        'shipping_address_id': shipping_id,  # 👈 required for webhook handler
    }

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
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
    except stripe.error.StripeError:
        alert(
            request,
            "error",
            "There was a problem connecting to the payment service."
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
    all_orders = Order.objects.select_related("shipping_address").filter(
        user=request.user
    ).order_by('-order_date')    
    print("DEBUG: ORDER HISTORY")
    for o in all_orders:
        print(f"Order {o.id} | sub_id={o.stripe_subscription_id} | created={o.order_date}")
    payments = Payment.objects.filter(order__in=all_orders)
    subscriptions = StripeSubscriptionMeta.objects.filter(user=request.user)
    sub_map = {
        sub.stripe_subscription_id: {
            'sub': sub,
            'label': get_subscription_duration_display(sub),
            'status': get_subscription_status(sub),
        } for sub in subscriptions
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

    if authenticate(username=request.user.username, password=password):
        try:
            sub = StripeSubscriptionMeta.objects.filter(
                user=request.user,
                cancelled_at__isnull=True
            ).latest('created_at')

            if not sub.stripe_subscription_id:
                return JsonResponse({
                    'success': False, 'error': 'No Stripe subscription found.'
                })

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
                f"Subscription cancelled for user {request.user}"
            )
            return JsonResponse({
                'success': True,
                'message': 'Subscription will cancel at period end.'
            })

        except StripeSubscriptionMeta.DoesNotExist:
            logger.warning(
                f"{request.user} "
                f"tried to cancel but no active subscription found"
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

        logger.info(
            f"{request.user} selected shipping address ID "
            f"{selected_id} for plan {plan}, gift={gift}"
        )
        request.session['checkout_shipping_id'] = int(selected_id)

        if gift:
            return redirect('gift_message', plan=plan)
        if plan == "oneoff":
            return redirect('handle_purchase_type', plan='oneoff')

        return redirect('handle_purchase_type', plan=plan)

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
