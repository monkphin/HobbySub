"""
users/urls.py

Defines URL patterns for user account management, authentication,
address handling, and webhook interactions.
"""

from django.urls import path
from users import views

urlpatterns = [
    # Authentication & Signup Flow Overrides
    path("accounts/signup/", views.CustomSignupView.as_view(), name="account_signup"),
    path("accounts/confirm-email/<key>/", views.CustomConfirmEmailView.as_view(), name="account_confirm_email"),

    # Signup Entry Points
    path("start-subscription/", views.start_subscription, name="start_subscription"),
    path("start-gift/", views.start_gift, name="start_gift"),

    # Account Management
    path("account/", views.account_view, name="account"),
    path("edit/", views.edit_account, name="edit_account"),
    path("change_password/", views.change_password, name="change_password"),
    path("secure_change_email/", views.secure_change_email, name="change_email"),
    path("secure_delete_account/", views.secure_delete_account, name="secure_delete_account"),

    # Address Management
    path("address/add/", views.add_address, name="add_address"),
    path("address/<int:address_id>/edit/", views.edit_address, name="edit_address"),
    path("address/<int:address_id>/set_default/", views.set_default_address, name="set_default_address"),
    path("secure_delete_address/<int:address_id>/", views.secure_delete_address, name="secure_delete_address"),

    # Stripe Webhooks
    path("stripe_webhook/", views.stripe_webhook, name="stripe_webhook"),
]
