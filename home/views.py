"""
Contains view logic for public-facing pages:
 - Homepage with current and upcoming box info
 - Subscription options
 - About and Contact pages
"""

# Django/External Imports
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.signing import BadSignature
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.shortcuts import redirect
from django.contrib.auth import login
from django.shortcuts import render
from django.contrib import messages
from datetime import date
import logging





# Local Imports
from boxes.models import Box
from .forms import Register

from hobbyhub.mail import send_registration_email


logger = logging.getLogger(__name__)
signer = Signer()


def home(request):
    """
    Renders the homepage with:
    - The most recently shipped box (if available)
    - Its contents
    - The next upcoming box (based on month/year)
    """
    today = date.today()

    # Current box if it has already shipped
    box = Box.objects.filter(
        is_archived=False,
        shipping_date__lte=today
        ).order_by('-shipping_date').first()
    
    box_contents = box.products.all() if box else []

    # Determine the next month and year
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year

    # Upcoming box (next month's box)
    next_box = Box.objects.filter(
        is_archived=False,
        shipping_date__year=next_year,
        shipping_date__month=next_month
    ).first()

    return render(request, 'home/index.html', {
        'box': box,
        'box_contents': box_contents,
        'next_box': next_box
    })


def subscribe_options(request):
    """
    Renders the subscription options page.
    """
    return render(request, 'orders/subscribe.html')


def about(request):
    """
    Renders the About page.
    """
    return render(request, 'home/about.html')


def register_user(request):
    next_url = request.GET.get('next')  # get ?next param
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_registration_email(user, next_url)
            request.session['post_confirm_redirect'] = next_url  # store it
            logger.info(f"Registration successful for {user.email}, confirmation sent")
            messages.success(request, "Registration successful! Please check your email and click the confirmation link to activate your account.")
            request.session['registered_email'] = user.email
            return redirect('check_email')
    else:
        form = Register()

    return render(request, 'home/register.html', {
        'form': form,
        'next': next_url
    })


def check_email(request):
    """
    Renders a page instructing the user to check their email for verification.
    """
    email = request.session.get('registered_email', None)  # Get from session
    if email:
        request.session['registered_email'] = email  # Put it back so it stays
    
    return render(request, 'home/check_email.html', {
        'email': email
    })


def confirm_email(request, token):
    try:
        user_id = signer.unsign(token)
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        login(request, user)

        # First try session-based redirect
        next_url = request.session.pop('post_confirm_redirect', None)

        # If not found in session, fall back to query param
        if not next_url:
            next_url = request.GET.get('next')

        messages.success(request, "Email confirmed! You're now logged in.")

        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
            return redirect(next_url)

        return redirect('home')

    except (BadSignature, User.DoesNotExist):
        messages.error(request, "Invalid or expired confirmation link.")
        return redirect('home')
    

def resend_activation(request):
    email = request.GET.get('email')
    try:
        user = User.objects.get(email=email)
        if not user.is_active:
            send_registration_email(user, request.session.get('post_confirm_redirect'))
            messages.success(request, "Activation email resent. Please check your inbox.")
    except User.DoesNotExist:
        messages.error(request, "No account found with that email.")
    
    return redirect('check_email')