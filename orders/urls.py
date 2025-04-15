# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('gift/', views.order_gift, name='order_gift'),
    path('oneoff/', views.order_oneoff, name='order_oneoff'),
    path('subscribe/monthly/', views.create_monthly_subscription, name='create_monthly_subscription'),
    path('success/', views.order_success, name='order_success'),
    path('cancel/', views.order_cancel, name='order_cancel'),
    path('history/', views.order_history, name='order_history'),
]
