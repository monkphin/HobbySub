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
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/subscribe/<str:plan>/', views.create_subscription, name='create_subscription'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),

    # Checkout outcomes'
    path('success/', views.order_success, name='order_success'),
    path('cancel/', views.order_cancel, name='order_cancel'),
    path('history/', views.order_history, name='order_history'),
]
