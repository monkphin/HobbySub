"""
users/views.py

Handles user registration, authentication, account management, 
shipping address operations, password changes, and Stripe webhooks.
"""

# Django/External imports 
from django.contrib.auth import login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import stripe.error
import logging
import stripe


# Local imports
from hobbyhub.mail import (
    send_registration_email,
    send_account_update_email,
    send_address_change_email,
    send_account_deletion_email    
    )
from hobbyhub.stripe_handlers import (
    handle_checkout_session_completed,
    handle_invoice_payment_succeeded,
    handle_invoice_payment_failed,
    handle_invoice_upcoming,
)
from .forms import Register, AddAddressForm, ChangePassword
from .models import ShippingAddress
from hobbyhub.utils import alert

logger = logging.getLogger(__name__)


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
            logger.info(f"New user registered and logged in: {user.email}")
            alert(
                request,
                "success",
                "Your account has been created and you're now logged in."
                )

            return redirect('home')
    else:
        form = Register()
        if request.method == 'POST':
            logger.warning("Registration form invalid")
        
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
            logger.info(f"{request.user} changed their password")
            alert(
                request,
                "success",
                "Your password has been changed successfully."
                )
            return redirect('account')
    else:
        form = ChangePassword()

    return render(request, 'users/change_password.html', {'form': form})

@require_POST
@login_required
def delete_account(request):
    """
    Deletes the currently logged-in user’s account.
    Logs them out before deletion.
    """
    user = request.user
    logger.info(f"Account deletion triggered for {user.email}")
    alert(
        request,
        "info",
        "Your account has been deleted. We're sorry to see you go!"
        )
    logout(request)
    send_account_deletion_email(user.email)
    user.delete()
    logger.warning(f"User account deleted: {user.email}")
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
            logger.info(f"{request.user} added new address — default={address.is_default}")
            send_address_change_email(request.user, change_type="added")
            alert(request, "success", "Address added successfully.")

            # Check if we're returning to a gift flow
            if 'return_to_gift' in request.session:
                plan = request.session.pop('return_to_gift')
                return redirect('gift_message', plan=plan)

            # Otherwise, follow next_url if safe
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
            logger.info(f"{request.user} updated address {address_id}")
            send_address_change_email(request.user, change_type="updated")
            alert(request, "success", "Address updated successfully.")
            return redirect('account')
    else:
        form = AddAddressForm(instance=address)

    return render(request, 'users/add_address.html', {'form': form})

@require_POST
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
    logger.info(f"{user} set address {address_id} as default")
    return redirect('account')

@require_POST
@login_required
def delete_address(request, address_id):
    """
    Deletes a user's shipping address.
    """
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    send_address_change_email(request.user, change_type="deleted")
    alert(request, "info", "Address deleted.")
    logger.info(f"{request.user} deleted address {address_id}")
    return redirect('account')


@csrf_exempt
def stripe_webhook(request):
    logger.info("Stripe webhook received")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        logger.warning("Invalid webhook signature or payload")
        return HttpResponse(status=400)

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        handle_checkout_session_completed(data)
    elif event_type == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(data)
    elif event_type == 'invoice.payment_failed':
        handle_invoice_payment_failed(data)
    elif event_type == 'invoice.upcoming':
        handle_invoice_upcoming(data)
    else:
        logger.info(f"Ignored event type: {event_type}")


    return JsonResponse({'status': 'success'})