"""
orders/views.py

Handles order and checkout flows including:
- Gift and one-off purchases
- Stripe subscription plans
- Checkout success/cancel pages
- Order history display
"""
# Django/External Imports
import stripe 
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# LOcal imports
from .forms import PreCheckoutForm
from .models import Order
from hobbyhub.utils import alert

# Configure Stripe with secret API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Price IDs from settings
GIFT_PRICE_ID = settings.STRIPE_GIFT_PRICE_ID
ONEOFF_PRICE_ID = settings.STRIPE_ONEOFF_PRICE_ID
STRIPE_MONTHLY_PRICE_ID = settings.STRIPE_MONTHLY_PRICE_ID
STRIPE_3MO_PRICE_ID = settings.STRIPE_3MO_PRICE_ID
STRIPE_6MO_PRICE_ID = settings.STRIPE_6MO_PRICE_ID
STRIPE_12MO_PRICE_ID = settings.STRIPE_12MO_PRICE_ID


@login_required
def order_success(request):
    """
    Renders the order success page with a success message.
    """
    alert(request, "success", "Your order was successfully processed. Thank you!")
    return render(request, 'orders/order_success.html')


@login_required
def order_cancel(request):
    """
    Renders the order cancellation page with an info message.
    """
    alert(request, "info", "Your checkout was cancelled, no payment has been taken")
    return render(request, 'orders/order_cancel.html')


@login_required
def order_gift(request):
    """
    Starts checkout for a gift order.
    """
    return handle_checkout(request, price_id=GIFT_PRICE_ID)


@login_required
def order_oneoff(request):
    """
    Starts checkout for a one-off order.
    """
    return handle_checkout(request, price_id=ONEOFF_PRICE_ID)


@login_required
def create_monthly_subscription(request):
    """
    Starts checkout for a monthly subscription.
    """
    return create_subscription_checkout(request, STRIPE_MONTHLY_PRICE_ID)


@login_required
def create_3mo_subscription(request):
    """
    Starts checkout for a 3-month subscription.
    """
    return create_subscription_checkout(request, STRIPE_3MO_PRICE_ID)


@login_required
def create_6mo_subscription(request): 
    """
    Starts checkout for a 6-month subscription.
    """
    return create_subscription_checkout(request, STRIPE_6MO_PRICE_ID)


@login_required
def create_12mo_subscription(request): 
    """
    Starts checkout for a 12-month subscription.
    """
    return create_subscription_checkout(request, STRIPE_12MO_PRICE_ID)


def handle_checkout(request, price_id):
    """
    Handles checkout for gift or one-off purchases.
    Validates pre-checkout form and creates Stripe checkout session.
    """
    if request.method == 'POST':
        form = PreCheckoutForm(request.POST)

        if form.is_valid():
            recipient_name = form.cleaned_data.get('recipient_name')
            sender_name = form.cleaned_data.get('sender_name')
            gift_message = form.cleaned_data.get('gift_message')

            shipping_address = request.user.addresses.filter(is_default=True).first()

            if not shipping_address:
                alert(request, "error", "You must set a default shipping address before placing an order.")
                return redirect('account_settings')

            shipping_details = {
                'name': f'{shipping_address.recipient_f_name} {shipping_address.recipient_l_name}',
                'address': {
                    'line1': shipping_address.address_line_1,
                    'line2': shipping_address.address_line_2 or '',
                    'city': shipping_address.town_or_city,
                    'state': shipping_address.county,
                    'postal_code': shipping_address.postcode,
                    'country': shipping_address.country,
                }
            }
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[{
                        'price': price_id,
                        'quantity': 1,
                    }],
                    payment_intent_data={
                        'metadata': {
                            'recipient_name': recipient_name,
                            'sender_name': sender_name,
                            'gift_message': gift_message,
                            'user_id': str(request.user.id),
                        },
                        'shipping': shipping_details
                    },
                    customer_email=request.user.email,
                    success_url=request.build_absolute_uri('/orders/success/'),
                    cancel_url=request.build_absolute_uri('/orders/cancel/'),
                )
                return redirect(session.url, code=303)
            except stripe.error.StripeError:
                alert(request, "error", "There was a problem connecting to the payment service. Please try again shortly.")
                return render(request, 'orders/pre_checkout.html', {'form': form})
        else:
            alert(request, "error", "Please correct the errors in the form.")
    else:
        form = PreCheckoutForm()

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
    """
    Displays a list of past orders for the current user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    if not orders.exists():
        alert(request, "info", "You haven’t placed any orders yet.")
    return render(request, 'orders/order_history.html', {'orders': orders})