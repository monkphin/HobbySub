"""
dashboard/urls.py

Defines URL patterns for custom admin dashboard views.
Includes management routes for boxes, products, and users.
"""
# Django Imports
from django.urls import path

# Local Imports
from . import views


urlpatterns = [
    # Box admin
    path('box_admin/', views.box_admin, name='box_admin'),
    path('add_box/', views.add_box, name='add_box'),
    path('box_admin/<int:box_id>/edit/', views.edit_box, name='edit_box'),
    path(
        'box_admin/<int:box_id>/delete/',
        views.delete_box,
        name='delete_box'
    ),
    path(
        'box_admin/<int:box_id>/products/',
        views.edit_box_products, name='edit_box_products'
    ),
    path(
        'box_admin/<int:box_id>/products/add/',
        views.add_product_to_box, name='add_product_to_box'
    ),

    # Product Admin
    path('products/add/', views.add_products, name='add_products'),
    path(
        'products/<int:product_id>/edit/',
        views.edit_product,
        name='edit_product'
    ),
    path(
        'products/<int:product_id>/delete/',
        views.delete_product,
        name='delete_product'
    ),
    path(
        'products/<int:product_id>/remove/',
        views.remove_product_from_box,
        name='remove_product_from_box'
    ),

    # User admin
    path('user_admin/', views.user_admin, name='user_admin'),
    path('user_admin/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path(
        'user_admin/<int:user_id>/delete/',
        views.delete_user,
        name='delete_user'
    ),
    path(
        'user_admin/<int:user_id>/orders/',
        views.user_orders,
        name='user_orders'
    ),
    path(
        'order/<int:order_id>/update_status/',
        views.update_order_status,
        name='update_order_status'
    ),
]
