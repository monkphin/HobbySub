"""
users/urls.py

Defines URL patterns for user account management, authentication,
address handling, and webhook interactions.
"""

# DJango/remote imports
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
# Local imports
from .views import change_email, secure_delete_account, secure_delete_address

urlpatterns = [
    # Authentication
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Account Management
    path('account/', views.account_view, name='account'),
    path('edit/', views.edit_account, name='edit_account'),
    path('change-email/', change_email, name='change_email'),
    path(
        'secure_delete_account/',
        secure_delete_account,
        name='secure_delete_account'
    ),
    path('change_password/', views.change_password, name='change_password'),

    # Address Management
    path('address/add/', views.add_address, name='add_address'),
    path(
        'address/<int:address_id>/edit/',
        views.edit_address,
        name='edit_address'
    ),
    path(
        'address/<int:address_id>/set_default/',
        views.set_default_address,
        name='set_default_address'
    ),
    path(
        'secure_delete_address/<int:address_id>/',
        secure_delete_address,
        name='secure_delete_address'
    ),

    # Stripe Webhooks
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),

    # Password resets
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
