"""
# home/urls.py

Defines URL patterns for the public site.
Includes views for home, about, contact, and subscription options.
"""

from django.urls import path
from . import views

# URL patterns for public facing views within the home app
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe_options, name='subscribe_options'),
]
