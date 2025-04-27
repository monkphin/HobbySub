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
    # Unified entry point for orders
    path('start/', views.order_start, name='order_start'),
    path('select/', views.select_purchase_type, name='select_purchase_type'),
    path('purchase/<str:plan>/', views.handle_purchase_type, name='handle_purchase_type'),
    path('gift/message/<str:plan>/', views.gift_message, name='gift_message'),

    # Subscription Cancellation
    path('secure_cancel_subscription/', views.secure_cancel_subscription, name='secure_cancel_subscription'),

    # Checkout outcomes'
    path('success/', views.order_success, name='order_success'),
    path('cancel/', views.order_cancel, name='order_cancel'),
    path('history/', views.order_history, name='order_history'),
    path('shipping/select/<str:plan>/', views.choose_shipping_address, name='choose_shipping_address'),
]
