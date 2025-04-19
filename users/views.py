"""
users/views.py

Handles user registration, authentication, account management, 
shipping address operations, password changes, and Stripe webhooks.
"""

# Django/Remote imports 
from django.contrib.auth import login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import stripe.error
import stripe

# Local imports
from .models import ShippingAddress
from orders.models import Order, Payment, Box, StripeSubscriptionMeta
from .forms import Register, AddAddressForm, ChangePassword
from hobbyhub.utils import alert


def register_user(request):
    """
    Registers a new user and logs them in immediately.
    Renders the registration form and handles POST submissions.
    """
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login on registration
            login(request, user) 
            alert(
                request,
                "success",
                "Your account has been created and you're now logged in."
                )

            return redirect('home')
    else:
        form = Register()
        
    return render(request, 'users/register.html', {'form': form})


@login_required
def account_view(request):
    """
    Displays the user's account dashboard.
    """
    return render(request, 'users/account.html')


@login_required
def edit_account(request):
    """
    Allows the user to update their account information.
    """
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            alert(request, "success", "Your account details have been updated.")
            return redirect('account')
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'users/edit_account.html', {'form':form})


@login_required
def change_password(request):
    """
    Lets the user change their password securely.
    """
    if request.method == 'POST':
        form = ChangePassword(request.POST)
        if form.is_valid():
            form.save(request.user)
            update_session_auth_hash(request, request.user)
            alert(
                request,
                "success",
                "Your password has been changed successfully."
                )
            return redirect('account')
    else:
        form = ChangePassword()

    return render(request, 'users/change_password.html', {'form': form})


@login_required
def delete_account(request):
    """
    Deletes the currently logged-in user’s account.
    Logs them out before deletion.
    """
    user = request.user
    alert(
        request,
        "info",
        "Your account has been deleted. We're sorry to see you go!"
        )
    logout(request)
    user.delete()
    return redirect('account')


@login_required
def add_address(request):
    """
    Allows the user to add a new shipping address.
    If marked as default, unsets all other default addresses.
    Redirects to the URL provided in 'next' query parameter (if valid),
    or falls back to 'account'.
    """
    next_url = request.GET.get('next', request.POST.get('next', 'account'))

    if request.method == 'POST':
        form = AddAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                ShippingAddress.objects.filter(
                    user=request.user,
                    is_default=True
                    ).update(is_default=False)
            address.save()
            alert(request, "success", "Address added successfully.")

            # Only redirect to a safe URL
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('account')  # fallback

    else:
        form = AddAddressForm(initial={
            'recipient_f_name': request.user.first_name,
            'recipient_l_name': request.user.last_name,
        })

    return render(request, 'users/add_address.html', {
        'form': form,
        'next': next_url  # pass this to the template
    })

@login_required
def edit_address(request, address_id):
    """
    Edits an existing shipping address for the user.
    Updates default address status if necessary.
    """
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddAddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)

            if updated_address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)

            updated_address.save()
            alert(request, "success", "Address updated successfully.")
            return redirect('account')
    else:
        form = AddAddressForm(instance=address)

    return render(request, 'users/add_address.html', {'form': form})


@login_required
def set_default_address(request, address_id):
    """
    Sets the selected address as the user's default.
    Unsets any previously marked default address.
    """
    user = request.user
    address = get_object_or_404(ShippingAddress, id=address_id, user=user)
    # Unset existing default
    ShippingAddress.objects.filter(user=user, is_default=True).update(is_default=False)
    # Set the new default address
    address.is_default=True
    address.save()
    alert(request, "success", "Default address updated.")
    return redirect('account')


@login_required
def delete_address(request, address_id):
    """
    Deletes a user's shipping address.
    """
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    alert(request, "info", "Address deleted.")
    return redirect('account')


@csrf_exempt
def stripe_webhook(request):
    """
    Handles incoming Stripe webhook events for orders and subscriptions.
    Supports `checkout.session.completed` and `invoice.payment_succeeded`.
    """
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
        print("Event type:", event['type'])

        payment_intent_id = session.get('payment_intent')
        user_id = session.get('metadata', {}).get('user_id')

        if payment_intent_id:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            metadata = payment_intent.metadata
            shipping_info = payment_intent.shipping
            user_id = metadata.get('user_id')

            print("Shipping info:", shipping_info)
            print("Metadata:", metadata)

            if user_id and shipping_info:
                try:
                    user = User.objects.get(pk=user_id)
                    address = ShippingAddress.objects.filter(user=user, postcode=shipping_info['address']['postal_code']).first()

                    print("Looking for ShippingAddress with postcode:", shipping_info['address']['postal_code'])
                    print("User:", user)
                    print("Found address:", address)

                    Order.objects.create(
                        user=user,
                        shipping_address=address,
                        box=None,
                        stripe_subscription_id=session.get('subscription'),
                        scheduled_shipping_date=None,
                        status='processing'
                    )
                    print("Order created successfully")

                except User.DoesNotExist:
                    print(f"User ID {user_id} not found")
                except Exception as e:
                    print(f"Error creating order: {e}")
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
                print("Subscription saved for:", user.username)
            except Exception as e:
                print(f"Subscription handling error: {e}")

    elif event['type'] == 'invoice.payment_succeeded':
        print("Received invoice.payment_succeeded")
        invoice = event['data']['object']
        print("Payment succeeded for subscription")

        subscription_id = invoice.get('subscription')
        customer_id = invoice.get('customer') 
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.get('email')
        amount_paid = invoice['amount_paid'] / 100  # convert from cents
        payment_date = timezone.now()

        try:
            print("Looking for user and sub")
            user = User.objects.get(email=customer_email)
            sub_meta = StripeSubscriptionMeta.objects.filter(
                user=user, stripe_subscription_id=subscription_id
            ).first()

            # Fallback shipping logic
            shipping = None
            if sub_meta and sub_meta.shipping_address:
                shipping = sub_meta.shipping_address
            else:
                shipping = user.addresses.filter(is_default=True).first() or user.addresses.first()

            if not shipping:
                print(f"No valid shipping address found for user {user.username}")
                return JsonResponse({'status': 'no shipping address'}, status=200)

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
                order_id=order.id,
                payment_date=payment_date,
                amount=amount_paid,
                status='succeeded',
                payment_method='card',
            )

            print(f"Created order + payment for {user.username}")

        except Exception as e:
            print(f"Failed to create recurring order/payment: {e}")

    return JsonResponse({'status': 'success'})