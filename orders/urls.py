"""
orders/urls.py

Defines URL patterns for the orders app.
Includes routes for one-off orders, subscriptions, order history, and checkout outcomes.
"""
# Django imports
from django.urls import path

# Local imports 
from . import views

urlpatterns = [
    # One off gifts/orders.
    path('gift/', views.order_gift, name='order_gift'),
    path('oneoff/', views.order_oneoff, name='order_oneoff'),

    # Subscriptions.
    path('subscribe/monthly/', views.create_monthly_subscription, name='create_monthly_subscription'),
    path('subscribe/3months/', views.create_3mo_subscription, name='create_3mo_subscription'),
    path('subscribe/6months/', views.create_6mo_subscription, name='create_6mo_subscription'),
    path('subscribe/12months/', views.create_12mo_subscription, name='create_12mo_subscription'),

    # Checkout outcomes'
    path('success/', views.order_success, name='order_success'),
    path('cancel/', views.order_cancel, name='order_cancel'),
    path('history/', views.order_history, name='order_history'),
]
