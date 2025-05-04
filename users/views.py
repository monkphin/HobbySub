"""
users/views.py

Handles user registration, authentication, account management,
shipping address operations, password changes, and Stripe webhooks.
"""

# Django/External imports
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView, SignupView
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views import View
import stripe
import stripe.error
import logging
import json

# Local imports
from hobbyhub.mail import send_account_update_email, send_address_change_email
from hobbyhub.stripe_handlers import (
    handle_checkout_session_completed,
    handle_invoice_payment_succeeded,
    handle_invoice_payment_failed,
    handle_invoice_upcoming,
)
from .forms import AddAddressForm, ChangePassword, UserEditForm
from .models import ShippingAddress
from hobbyhub.utils import alert

logger = logging.getLogger(__name__)

# ------------------------------
# Signup + Email Flow Overrides
# ------------------------------

class CustomSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        print("CustomSignupView dispatch GET params:", request.GET.dict())
        print("Session keys:", list(request.session.keys()))

        if 'next' in request.GET:
            request.GET._mutable = True
            del request.GET['next']
            request.GET._mutable = False
        request.session.pop('account_verified_email_next', None)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        gift = self.request.session.pop("gift_purchase", False)
        return reverse("select_purchase_type") + ("?gift=true" if gift else "?gift=false")


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(request)
        return render(request, "account/email/email_confirmed.html")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


# ------------------------------
# Entry Points
# ------------------------------

def start_subscription(request):
    request.session["gift_purchase"] = False
    return redirect(reverse("account_signup"))

def start_gift(request):
    request.session["gift_purchase"] = True
    return redirect("account_signup")

# ------------------------------
# Authenticated User Views
# ------------------------------

@login_required
def account_view(request):
    return render(request, 'users/account.html')


@login_required
def edit_account(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            send_account_update_email(request.user)
            alert(request, "success", "Your account details have been updated.")
            return redirect('account')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'users/edit_account.html', {'form': form})


@require_POST
@login_required
@csrf_exempt
def secure_change_email(request):
    data = json.loads(request.body)
    password = data.get('password')
    new_email = data.get('new_email')
    if not request.user.check_password(password):
        return JsonResponse({'success': False, 'error': 'Incorrect password'})
    if not new_email:
        return JsonResponse({'success': False, 'error': 'Email cannot be empty'})
    request.user.email = new_email
    request.user.save()
    send_address_change_email(request.user, change_type="updated")
    return JsonResponse({'success': True})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePassword(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            alert(request, "success", "Your password has been changed successfully.")
            return redirect('account')
    else:
        form = ChangePassword(user=request.user)
    return render(request, 'users/change_password.html', {'form': form})


@require_POST
@login_required
@csrf_exempt
def secure_delete_account(request):
    data = json.loads(request.body)
    password = data.get('password')
    if authenticate(username=request.user.username, password=password):
        logout(request)
        request.user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Incorrect password'})


# ------------------------------
# Address Management
# ------------------------------

@login_required
def add_address(request):
    next_url = request.GET.get('next', request.POST.get('next', 'account'))
    if request.method == 'POST':
        form = AddAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.save()
            if ShippingAddress.objects.filter(user=request.user).count() == 1:
                address.is_default = True
                address.save()
            send_address_change_email(request.user, change_type="added")
            alert(request, "success", "Address added successfully.")
            if 'return_to_gift' in request.session:
                plan = request.session.pop('return_to_gift')
                return redirect('gift_message', plan=plan)
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('account')
    else:
        form = AddAddressForm(initial={
            'recipient_f_name': request.user.first_name,
            'recipient_l_name': request.user.last_name,
        })
    return render(request, 'users/add_address.html', {'form': form, 'next': next_url})


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
            send_address_change_email(request.user, change_type="updated")
            alert(request, "success", "Address updated successfully.")
            return redirect('account')
    else:
        form = AddAddressForm(instance=address)
    return render(request, 'users/add_address.html', {'form': form})


@require_POST
@login_required
def set_default_address(request, address_id):
    user = request.user
    address = get_object_or_404(ShippingAddress, id=address_id, user=user)
    ShippingAddress.objects.filter(user=user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    send_address_change_email(request.user, change_type="default")
    alert(request, "success", "Default address updated.")
    return redirect('account')


@require_POST
@login_required
@csrf_exempt
def secure_delete_address(request, address_id):
    data = json.loads(request.body)
    password = data.get('password')
    if authenticate(username=request.user.username, password=password):
        address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Incorrect password'})


# ------------------------------
# Stripe Webhook
# ------------------------------

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
