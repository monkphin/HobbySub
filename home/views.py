"""
Contains view logic for public-facing pages:
 - Homepage with current and upcoming box info
 - Subscription options
 - About and Contact pages
"""

# Django/External Imports
from django.shortcuts import render
from datetime import date

# Local Imports
from boxes.models import Box

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


def contact(request):
    """
    Renders the Contact page.
    """
    return render(request, 'home/contact.html')
