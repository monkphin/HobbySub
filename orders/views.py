import stripe 
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import PreCheckoutForm


stripe.api_key = settings.STRIPE_SECRET_KEY
GIFT_PRICE_ID = settings.STRIPE_GIFT_PRICE_ID
ONEOFF_PRICE_ID = settings.STRIPE_ONEOFF_PRICE_ID

@login_required
def order_success(request):
    return render(request, 'orders/order_success.html')


@login_required
def order_cancel(request):
    return render(request, 'orders/order_cancel.html')


@login_required
def order_gift(request):
    return handle_checkout(request, price_id=GIFT_PRICE_ID)


@login_required
def order_oneoff(request):
    return handle_checkout(request, price_id=ONEOFF_PRICE_ID)


def handle_checkout(request, price_id):
    if request.method == 'POST':
        form = PreCheckoutForm(request.POST)
        if form.is_valid():
            recipient_name = form.cleaned_data.get('recipient_name')
            sender_name = form.cleaned_data.get('sender_name')
            gift_message = form.cleaned_data.get('gift_message')

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price':price_id,
                    'quantity': 1,
                }],
                payment_intent_data={
                    'metadata': {
                        'recipient_name': recipient_name,
                        'sender_name': sender_name, 
                        'gift_message': gift_message,
                        'user_id': str(request.user.id),
                    }
                },
                customer_email=request.user.email,
                success_url=request.build_absolute_uri('/orders/success/'),
                cancel_url=request.build_absolute_uri('/orders/cancel/'),
            )
            return redirect(session.url, code=303)
    else:
        form = PreCheckoutForm()
    
    return render(request, 'orders/pre_checkout.html',{'form':form})