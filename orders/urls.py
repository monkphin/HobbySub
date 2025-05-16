"""
orders/urls.py

Defines URL patterns for the orders app.
Includes routes for one-off orders, subscriptions, order history, and checkout outcomes.
"""
# Django imports
from django.urls import path

# Local imports 
from . import views
from .views import select_purchase_type, handle_purchase_type, gift_message, secure_cancel_subscription, order_success, order_cancel, order_history


urlpatterns = [
    # Unified entry point for orders
    path('select/', select_purchase_type, name='select_purchase_type'),
    path('purchase/<str:plan>/', handle_purchase_type, name='handle_purchase_type'),
    path('gift/message/<str:plan>/', gift_message, name='gift_message'),

    # Subscription Cancellation
    path('secure_cancel_subscription/', secure_cancel_subscription, name='secure_cancel_subscription'),

    # Checkout outcomes'
    path('success/', order_success, name='order_success'),
    path('cancel/', order_cancel, name='order_cancel'),
    path('history/', order_history, name='order_history'),
    path('shipping/select/<str:plan>/', views.choose_shipping_address, name='choose_shipping_address'),
]
