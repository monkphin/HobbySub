from django.contrib.auth import login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.conf import settings

import stripe
import json

import stripe.error

from .models import ShippingAddress
from orders.models import Order
from .forms import Register, AddAddressForm, ChangePassword


def register_user(request):
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto login on registration
            return redirect('home')
    else:
        form = Register()
        
    return render(request, 'users/register.html', {'form': form})

@login_required
def account_view(request):
    return render(request, 'users/account.html')

@csrf_exempt
def stripe_webhook(request):
    print("🚀 Stripe webhook received")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try: 
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("🎯 Event type:", event['type'])

        payment_intent_id = session.get('payment_intent')
        user_id = session.get('metadata', {}).get('user_id')

        from orders.models import StripeSubscriptionMeta
        if payment_intent_id:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            metadata = payment_intent.metadata
            shipping_info = payment_intent.shipping
            user_id = metadata.get('user_id')

            print("📦 Shipping info:", shipping_info)
            print("🧠 Metadata:", metadata)

            if user_id and shipping_info:
                try:
                    user = User.objects.get(pk=user_id)
                    address = ShippingAddress.objects.filter(user=user, postcode=shipping_info['address']['postal_code']).first()

                    print("🔍 Looking for ShippingAddress with postcode:", shipping_info['address']['postal_code'])
                    print("👤 User:", user)
                    print("📬 Found address:", address)

                    Order.objects.create(
                        user=user,
                        shipping_address=address,
                        box=None,
                        stripe_subscription_id=session.get('subscription'),
                        scheduled_shipping_date=None,
                        status='processing'
                    )
                    print("✅ Order created successfully")

                except User.DoesNotExist:
                    print(f"❌ User ID {user_id} not found")
                except Exception as e:
                    print(f"❌ Error creating order: {e}")
        elif session.get('mode') == 'subscription' and user_id: 
            try:
                user = User.objects.get(pk=user_id)
                shipping = user.addresses.filter(is_default=True).first()
                sub_id = session.get('subscription')
                subscription = stripe.Subscription.retrieve(sub_id)
                price_id = subscription['items']['data'][0]['price']['id']

                StripeSubscriptionMeta.objects.create(
                    user=user, 
                    stripe_subscription_id=sub_id,
                    stripe_price_id=price_id,
                    shipping_address=shipping,
                    is_gift=False,
                )
                print("✅ Subscription saved for:", user.username)
            except Exception as e:
                print(f"❌ Subscription handling error: {e}")

    return JsonResponse({'status': 'success'})



@login_required
def edit_account(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'users/edit_account.html', {'form':form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePassword(request.POST)
        if form.is_valid():
            form.save(request.user)
            update_session_auth_hash(request, request.user)
            return redirect('account')
    else:
        form = ChangePassword()

    return render(request, 'users/change_password.html', {'form': form})


@login_required
def delete_account(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('account')


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)

            address.save()
            return redirect('account')
    else:
        form = AddAddressForm(initial={
            'recipient_f_name': request.user.first_name,
            'recipient_l_name': request.user.last_name,
        })

    return render(request, 'users/add_address.html', {'form': form})


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddAddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)

            if updated_address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)

            updated_address.save()
            return redirect('account')
    else:
        form = AddAddressForm(instance=address)

    return render(request, 'users/add_address.html', {'form': form})



@login_required
def set_default_address(request, address_id):
    user = request.user
    address = get_object_or_404(ShippingAddress, id=address_id, user=user)

    # Unset existing default
    ShippingAddress.objects.filter(user=user, is_default=True).update(is_default=False)

    # Set the new default address
    address.is_default=True
    address.save()

    return redirect('account')


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    return redirect('account')
