"""
users/views.py

Handles user account management,
shipping address operations, password changes, and Stripe webhooks.
"""

import json
import logging
from urllib.parse import parse_qs, urlparse

import stripe
from django.conf import settings
from django.contrib import messages

from django.contrib.auth import (
    get_user_model,
    authenticate,
    logout,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.signing import Signer
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_str

from django.utils.http import (
    url_has_allowed_host_and_scheme,
    urlsafe_base64_decode
)

from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

from hobbyhub.mail import (
    send_account_deletion_email,
    send_account_update_email,
    send_address_change_email,
    send_email_change_notifications,
    send_password_change_email,
    send_password_reset_email
)

from hobbyhub.stripe_handlers import (
    handle_checkout_session_completed,
    handle_invoice_payment_failed,
    handle_invoice_payment_succeeded,
    handle_invoice_upcoming
)

from hobbyhub.utils import alert

from .forms import (
    AddAddressForm,
    ChangePassword,
    PasswordResetRequestForm,
    SetNewPasswordForm,
    UserEditForm
)
from .models import ShippingAddress

logger = logging.getLogger(__name__)
User = get_user_model()
signer = Signer()


@login_required
def account_view(request):
    """
    Displays the user's account dashboard.
    """
    user = request.user
    addresses = user.addresses.all()

    personal_addresses = (
        addresses.filter(is_gift_address=False).order_by('-is_default')
    )
    gift_addresses = addresses.filter(is_gift_address=True)

    context = {
        'personal_addresses': personal_addresses,
        'gift_addresses': gift_addresses,
    }
    return render(request, 'users/account.html', context)


@login_required
def edit_account(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            send_account_update_email(request.user)
            alert(
                request,
                "success",
                "Your account details have been updated."
            )
            return redirect('account')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'users/edit_account.html', {'form': form})


@csrf_protect
@login_required
@require_POST
def change_email(request):
    """
    Handles the user's email change process. Authenticates the user,
    updates the email, and sends confirmation notifications.
    """
    try:
        if request.content_type != 'application/json':
            return JsonResponse({
                'success': False,
                'error': f"Invalid content type: {request.content_type}"
            }, status=400)

        data = json.loads(request.body)
        new_email = data.get('new_email')
        password = data.get('password')

        if not new_email or not password:
            return JsonResponse(
                {
                    'success': False, 'error': 'Missing email or password.'
                }, status=400
            )

        user = authenticate(
            request,
            username=request.user.username,
            password=password
        )
        if user is None:
            return JsonResponse(
                {'success': False, 'error': 'Incorrect password.'},
                status=401
            )

        # Store the old email
        old_email = user.email
        user.email = new_email
        user.save()

        # CALLING THE FUNCTION FROM `mail.py`
        send_email_change_notifications(user, old_email, new_email)

        logger.info(
            f"Email change confirmed: {old_email} → {new_email} "
            f"for user {user.username}"
        )
        return JsonResponse({'success': True})

    except json.JSONDecodeError as e:
        return JsonResponse(
            {'success': False, 'error': f'JSON error: {str(e)}'}, status=400
        )


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePassword(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            alert(
                request,
                "success",
                "Your password has been changed successfully."
            )

            send_password_change_email(request.user)

            return redirect('account')
    else:
        form = ChangePassword(user=request.user)

    return render(request, 'users/change_password.html', {'form': form})


def password_reset_request(request):
    """
    Request password reset by entering an email.
    """
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                send_password_reset_email(user, domain=request.get_host())
            return redirect('password_reset_done')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    """
    Confirm the password reset and allow the user to set a new password.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data.get('new_password'))
                user.save()
                return redirect('password_reset_complete')
        else:
            form = SetNewPasswordForm()
        return render(
            request, 'users/password_reset_confirm.html', {'form': form}
        )
    else:
        return HttpResponse("Password reset link is invalid!", status=400)


def password_reset_done(request):
    """
    Inform the user that a password reset email has been sent.
    """
    return render(request, 'users/password_reset_done.html')


def password_reset_complete(request):
    """
    Inform the user that the password has been reset successfully.
    """
    return render(request, 'users/password_reset_complete.html')


@csrf_protect
@require_POST
@login_required
def secure_delete_account(request):
    data = json.loads(request.body)
    password = data.get('password')

    if request.user.check_password(password):
        user = request.user
        user_email = user.email
        try:
            logout(request)
            user.delete()
            send_account_deletion_email(user_email)
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(
                f"Account deletion failed for user {user.username}: {e}"
            )
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Deletion failed. Please try again.'
                },
                status=500
            )
    else:
        return JsonResponse({'success': False, 'error': 'Incorrect password'})


@login_required
def add_address(request):
    """
    Allows the user to add a new shipping address.
    If marked as default, unsets all other default addresses.
    Redirects to the URL provided in 'next' query parameter (if valid),
    or falls back to 'account'.
    """
    next_url = request.GET.get('next', request.POST.get('next', 'account'))
    gift = request.GET.get('gift', 'false').lower() == 'true'
    if not gift:
        parsed_next = parse_qs(urlparse(next_url).query)
        gift = parsed_next.get('gift', ['false'])[0].lower() == 'true'
    if request.method == 'POST':
        form = AddAddressForm(request.POST)

        if gift:
            # Don't let gift addresses be marked as default
            form.fields.pop('is_default', None)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.is_gift_address = gift

            if gift:
                address.is_default = False
            else:
                if address.is_default:
                    ShippingAddress.objects.filter(
                        user=request.user,
                        is_default=True
                    ).update(is_default=False)

                if not gift and not ShippingAddress.objects.filter(
                    user=request.user, is_default=True
                ).exists():
                    address.is_default = True

            address.save()

            logger.info(
                f"{request.user} added new address — "
                f"default={address.is_default}"
            )
            send_address_change_email(request.user, change_type="added")
            alert(request, "success", "Address added successfully.")

            if 'return_to_gift' in request.session:
                plan = request.session.pop('return_to_gift')
                return redirect('gift_message', plan=plan)

            # Ensure ?gift=true is preserved if this was a gift flow
            if gift and 'gift=true' not in next_url:
                separator = '&' if '?' in next_url else '?'
                next_url = f"{next_url}{separator}gift=true"

            if url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)

            return redirect('account')

    else:
        form = AddAddressForm(initial={
            'recipient_f_name': request.user.first_name,
            'recipient_l_name': request.user.last_name,
            'is_gift_address': gift
        })

    return render(request, 'users/add_address.html', {
        'form': form,
        'next': next_url,
        'gift': gift,
    })


@login_required
def edit_address(request, address_id):
    """
    Edits an existing shipping address for the user.
    Updates default address status if necessary.
    """
    address = get_object_or_404(
        ShippingAddress,
        id=address_id,
        user=request.user
    )

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == 'POST':
        form = AddAddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)

            if updated_address.is_default:
                ShippingAddress.objects.filter(
                    user=request.user,
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)

            updated_address.save()
            logger.info(f"{request.user} updated address {address_id}")
            send_address_change_email(request.user, change_type="updated")
            alert(request, "success", "Address updated successfully.")
            return redirect('account')
    else:
        form = AddAddressForm(instance=address)

    return render(request, 'users/add_address.html', {
        'form': form,
        'gift': address.is_gift_address,
        'next': next_url,
    })


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
    ShippingAddress.objects.filter(
        user=user,
        is_default=True
    ).update(is_default=False)
    # Set the new default address
    address.is_default = True
    address.save()
    send_address_change_email(request.user, change_type="default")
    alert(request, "success", "Default address updated.")
    logger.info(f"{user} set address {address_id} as default")
    return redirect('account')


@csrf_protect
@require_POST
@login_required
def secure_delete_address(request, address_id):
    data = json.loads(request.body)
    password = data.get('password')

    if not password:
        return JsonResponse(
            {'success': False, 'error': 'Password is required'},
            status=400
        )

    if authenticate(username=request.user.username, password=password):
        address = get_object_or_404(
            ShippingAddress,
            id=address_id,
            user=request.user
        )

        # Prevent deletion if the address is linked to active orders/subs
        if not address.can_be_deleted():
            return JsonResponse(
                {
                    'success': False,
                    'error': (
                        "This address is linked to an active order or "
                        "subscription and cannot be deleted."
                    )
                },
                status=400
            )

        was_default = address.is_default
        is_personal = not address.is_gift_address

        address.delete()

        send_address_change_email(
            request.user,
            change_type="removed from your account"
        )

        # If it was the default personal address, set a new one as default
        if was_default and is_personal:
            remaining = ShippingAddress.objects.filter(
                user=request.user,
                is_gift_address=False
            )
            if remaining.exists():
                new_default = remaining.first()
                new_default.is_default = True
                new_default.save()
                messages.info(
                    request,
                    "Your remaining address has been set as default."
                )

                send_address_change_email(
                    request.user,
                    change_type="set as your default"
                )

        return JsonResponse({'success': True})
    else:
        return JsonResponse(
            {'success': False, 'error': 'Incorrect password'},
            status=401
        )


@csrf_exempt
def stripe_webhook(request):
    logger.info("Stripe webhook received")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
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
