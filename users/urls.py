"""
users/urls.py

Defines URL patterns for user account management, authentication,
address handling, and webhook interactions.
"""

# DJango/remote imports
from django.contrib.auth import views as auth_views
from django.urls import path

# Local imports
from .views import secure_delete_account, secure_delete_address
from . import views


urlpatterns = [
        # Authentication
        path('register/', views.register_user, name='register'),
        path('confirm/<str:token>/', views.confirm_email, name='confirm_email'),
        path(
            'login/',
            auth_views.LoginView.as_view(
                template_name='users/login.html'
            ), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),

        # Account Management
        path('account/', views.account_view, name='account'),
        path('edit/', views.edit_account, name='edit_account'),
        path(
            'secure_delete_account/',
            secure_delete_account,
            name='secure_delete_account'
        ),
        path(
            'change_password/',
            views.change_password,
            name='change_password'
        ),

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
]
