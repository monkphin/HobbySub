# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
        path('register/', views.register_user, name='register'),
        path('account/', views.account_view, name='account'),
]
