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
from django.shortcuts import render, redirect
from django.conf import settings
import stripe 

# Local imports
from .models import Order
from .forms import PreCheckoutForm
from hobbyhub.utils import (
    alert,
    get_user_default_shipping_address,
    build_shipping_details,
    get_gift_metadata
)

# Configure Stripe with secret API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Price IDs from settings
GIFT_PRICE_ID = settings.STRIPE_GIFT_PRICE_ID
ONEOFF_PRICE_ID = settings.STRIPE_ONEOFF_PRICE_ID
STRIPE_MONTHLY_PRICE_ID = settings.STRIPE_MONTHLY_PRICE_ID
STRIPE_3MO_PRICE_ID = settings.STRIPE_3MO_PRICE_ID
STRIPE_6MO_PRICE_ID = settings.STRIPE_6MO_PRICE_ID
STRIPE_12MO_PRICE_ID = settings.STRIPE_12MO_PRICE_ID


def order_success(request):
    """
    Renders the order success page with a success message.
    """
    alert(request, "success", "Your order was successfully processed. Thank you!")
    return render(request, 'orders/order_success.html')


def order_cancel(request):
    """
    Renders the order cancellation page with an info message.
    """
    alert(request, "info", "Your checkout was cancelled, no payment has been taken")
    return render(request, 'orders/order_cancel.html')


def order_gift(request):
    """
    Starts checkout for a gift order.
    """
    return handle_checkout(request, price_id=GIFT_PRICE_ID)


def order_oneoff(request):
    """
    Starts checkout for a one-off order.
    """
    return handle_checkout(request, price_id=ONEOFF_PRICE_ID)


def subscribe(request):
    """
    Displays subscription plan options for the user to choose from.
    """
    return render(request, 'orders/subscribe.html')


def create_subscription(request, plan):
    plan_map = {
        "monthly": STRIPE_MONTHLY_PRICE_ID,
        "3mo": STRIPE_3MO_PRICE_ID,
        "6mo": STRIPE_6MO_PRICE_ID,
        "12mo": STRIPE_12MO_PRICE_ID,
    }
    price_id = plan_map.get(plan)
    if not price_id:
        alert(request, "error", "Invalid subscription plan.")
        return redirect('subscribe_options')

    return create_subscription_checkout(request, price_id)


@login_required
def handle_checkout(request, price_id):
    """
    Handles checkout for gift or one-off purchases.
    Validates pre-checkout form and creates Stripe checkout session.
    """
    form = PreCheckoutForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            shipping_address, redirect_response = get_user_default_shipping_address(request)
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
                    payment_intent_data={
                        'metadata': get_gift_metadata(form, request.user.id),
                        'shipping': build_shipping_details(shipping_address)
                    },
                    customer_email=request.user.email,
                    success_url=request.build_absolute_uri('/orders/success/'),
                    cancel_url=request.build_absolute_uri('/orders/cancel/'),
                )
                return redirect(session.url, code=303)
            except stripe.error.StripeError:
                alert(request, "error", "There was a problem connecting to the payment service. Please try again shortly.")
        else:
            alert(request, "error", "Please correct the errors in the form.")

    return render(request, 'orders/pre_checkout.html', {'form': form})


@login_required
def create_subscription_checkout(request, price_id):
    """
    Handles Stripe checkout session creation for subscription purchases.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            metadata={
                'user_id': request.user.id,
            },
            success_url=request.build_absolute_uri('/orders/success/?sub=monthly'),
            cancel_url=request.build_absolute_uri('/orders/cancel/'),
        )
        return redirect(checkout_session.url, code=303)
    except stripe.error.StripeError:
        alert(request, "error", "There was a problem connecting to the payment service. Please try again shortly.")
    return redirect('subscribe_options')


from orders.models import Order, Payment

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    payments = Payment.objects.filter(order__in=orders)

    # Map payments by order ID
    payments_by_order = {p.order_id: p for p in payments}

    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'payments_by_order': payments_by_order,
    })
