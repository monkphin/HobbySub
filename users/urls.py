# users/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
        path('register/', views.register_user, name='register'),
        path('account/', views.account_view, name='account'),
        path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('address/add/', views.add_address, name='add_address'),
        path('address/<int:address_id>/edit/', views.edit_address, name='edit_address'),

]
