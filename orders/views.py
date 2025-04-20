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
from django.utils import timezone
from django.conf import settings
import stripe 


# Local imports
from .forms import PreCheckoutForm
from hobbyhub.mail import send_subscription_cancelled_email
from .models import Order, Payment, StripeSubscriptionMeta
from hobbyhub.utils import (
    alert,
    get_user_default_shipping_address,
    build_shipping_details,
    get_gift_metadata,
    get_subscription_duration_display,
    get_subscription_status
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
def cancel_subscription(request):
    if request.method == 'POST':
        try:
            sub = StripeSubscriptionMeta.objects.filter(
                user=request.user,
                cancelled_at__isnull=True
            ).latest('created_at')
            if not sub.stripe_subscription_id:
                alert(request, "error", "No Stripe subscription found.")
                return redirect('order_history')

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
            alert(request, "success", "Your subscription will remain active until the end of your current billing period, then it will be cancelled.")
        except StripeSubscriptionMeta.DoesNotExist:
            alert(request, "error", "No active subscription found to cancel.")
    return redirect('order_history')


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
                    metadata=get_gift_metadata(form, request.user.id),
                    payment_intent_data={
                        'metadata': get_gift_metadata(form, request.user.id),
                        'shipping': build_shipping_details(shipping_address),
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


@login_required
def order_history(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-order_date')
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