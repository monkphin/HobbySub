from django.shortcuts import render
from boxes.models import Box
from datetime import date


def home(request):
    today = date.today()

    # Current box if shipped
    box = Box.objects.filter(is_archived=False, shipping_date__lte=today).order_by('-shipping_date').first()
    box_contents = box.products.all() if box else []

    # Next month’s box
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year

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
    return render(request, 'orders/subscribe.html')


def about(request):
    return render(request, 'home/about.html')


def contact(request):
    return render(request, 'home/contact.html')
