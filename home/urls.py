"""
# home/urls.py

Defines URL patterns for the public site.
Includes views for home, about, contact, and subscription options.
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import about, confirm_email, home, register_user, subscribe_options

# URL patterns for public facing views within the home app
urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('subscribe/', subscribe_options, name='subscribe_options'),
    path('register/', register_user, name='register'),
    path('check_email/', views.check_email, name='check_email'),
    path(
        'resend_activation/',
        views.resend_activation,
        name='resend_activation'
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='home/login.html'),
        name='login'
    ),
    path('confirm/<str:token>/', confirm_email, name='confirm_email'),
]
