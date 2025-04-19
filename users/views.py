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
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import stripe.error
import stripe

# Local imports
from orders.models import Order, Payment, Box, StripeSubscriptionMeta
from .forms import Register, AddAddressForm, ChangePassword
from hobbyhub.mail import send_gift_notification_to_recipient, send_registration_email, send_account_update_email, send_address_change_email, send_account_deletion_email, send_subscription_confirmation_email, send_gift_confirmation_to_sender, send_order_confirmation_email, send_payment_failed_email, send_upcoming_renewal_email
from .models import ShippingAddress
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
            send_registration_email(user)
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
            send_account_update_email(request.user)
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
    send_account_deletion_email(user.email)
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
            send_address_change_email(request.user, change_type="added")
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
            send_address_change_email(request.user, change_type="updated")
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
    send_address_change_email(request.user, change_type="default")
    alert(request, "success", "Default address updated.")
    return redirect('account')


@login_required
def delete_address(request, address_id):
    """
    Deletes a user's shipping address.
    """
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    send_address_change_email(request.user, change_type="deleted")
    alert(request, "info", "Address deleted.")
    return redirect('account')


@csrf_exempt
def stripe_webhook(request):
    print("🚀 Stripe webhook received")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        print("Invalid payload or signature")
        return HttpResponse(status=400)

    # ----------------------
    # One-off or Subscription Checkout
    # ----------------------
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Event type:", event['type'])

        payment_intent_id = session.get('payment_intent')
        user_id = session.get('metadata', {}).get('user_id')

        if payment_intent_id:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            metadata = payment_intent.metadata
            recipient_email = metadata.get('recipient_email')
            shipping_info = payment_intent.shipping
            user_id = metadata.get('user_id')
            amount_total = session.get('amount_total', 0)

            print("Shipping info:", shipping_info)
            print("Metadata:", metadata)
            print("Session amount_total:", amount_total)

            if user_id and shipping_info:
                try:
                    user = User.objects.get(pk=user_id)
                    address = ShippingAddress.objects.filter(
                        user=user, postcode=shipping_info['address']['postal_code']
                    ).first()

                    print("User:", user.username)
                    print("Found address:", address)

                    order = Order.objects.create(
                        user=user,
                        shipping_address=address,
                        box=None,
                        stripe_subscription_id=None,
                        scheduled_shipping_date=None,
                        status='processing'
                    )

                    print(f"Order #{order.id} created successfully")

                    Payment.objects.create(
                        user=user,
                        order=order,
                        payment_date=timezone.now(),
                        amount=amount_total / 100,
                        status='paid',
                        payment_method='card',
                    )

                    print(f"Payment recorded for one-off order #{order.id}")

                    # ✅ Email logic
                    if recipient_email:
                        send_gift_notification_to_recipient(
                            recipient_email=recipient_email,
                            sender_name=metadata.get('sender_name', 'Someone'),
                            gift_message=metadata.get('gift_message', '')
                        )
                        send_gift_confirmation_to_sender(user, recipient_email)
                        print(f"Gift email sent to {recipient_email}")
                    else:
                        send_order_confirmation_email(user, order.id)
                        print(f"Order confirmation sent to {user.email}")

                except User.DoesNotExist:
                    print(f"User ID {user_id} not found")
                except Exception as e:
                    print(f"Error creating order or payment: {e}")

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

                print(f"Subscription metadata saved for {user.username}")

                # ✅ Email logic
                send_subscription_confirmation_email(user, plan_name="Subscription Box")
                print(f"Subscription confirmation email sent to {user.email}")

            except Exception as e:
                print(f"Subscription handling error: {e}")

    # ----------------------
    # Recurring Subscription Payments
    # ----------------------
    elif event['type'] == 'invoice.payment_succeeded':
        print("Received invoice.payment_succeeded")
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        customer_id = invoice.get('customer')
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.get('email')
        amount_paid = invoice['amount_paid'] / 100
        payment_date = timezone.now()

        try:
            user = User.objects.get(email=customer_email)
            sub_meta = StripeSubscriptionMeta.objects.filter(
                user=user, stripe_subscription_id=subscription_id
            ).first()

            shipping = sub_meta.shipping_address if sub_meta and sub_meta.shipping_address else (
                user.addresses.filter(is_default=True).first() or user.addresses.first()
            )

            if not shipping:
                print(f"No shipping address found for {user.username}")
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
                order=order,
                payment_date=payment_date,
                amount=amount_paid,
                status='succeeded',
                payment_method='card',
            )

            print(f"Recurring order + payment created for {user.username}")
            # (You can optionally add a shipping confirmation email later)

        except Exception as e:
            print(f"Failed to create recurring order/payment: {e}")
    
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        customer_id = invoice.get('customer')
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.get('email')

        try:
            user = User.objects.get(email=customer_email)
            send_payment_failed_email(user)
            print(f"Payment failure email sent to {user.email}")
        except User.DoesNotExist:
            print(f"User with email {customer_email} not found")

    elif event['type'] == 'invoice.upcoming':
        invoice = event['data']['object']
        customer_id = invoice.get('customer')
        subscription_id = invoice.get('subscription')
        next_renewal_ts = invoice.get('next_payment_attempt')

        # Sometimes this is null
        if not next_renewal_ts:
            print("No next_payment_attempt found on invoice.upcoming")
            return JsonResponse({'status': 'ignored'})

        next_renewal = timezone.datetime.fromtimestamp(next_renewal_ts, tz=timezone.utc)
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.get('email')

        try:
            user = User.objects.get(email=customer_email)
            send_upcoming_renewal_email(user, next_renewal)
            print(f"Upcoming renewal email sent to {user.email}")
        except User.DoesNotExist:
            print(f"No user found for Stripe customer {customer_email}")


    return JsonResponse({'status': 'success'})
