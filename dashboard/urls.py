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
    path('dashboard/box/<int:box_id>/assign_orphaned/', views.assign_orphaned_to_box, name='assign_orphaned_to_box'),


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
    path('manage_orphaned_products/', views.manage_orphaned_products, name='manage_orphaned_products'),
    path('reassign_orphaned_products/<str:product_ids>/', views.reassign_orphaned_products, name='reassign_orphaned_products'),


    # User admin
    path('user_admin/', views.user_admin, name='user_admin'),
    path('user_admin/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user_admin/password-reset/<int:user_id>/', views.admin_initiated_password_reset, name='admin_password_reset'),
    path('user_admin/<int:user_id>/toggle-state/', views.admin_toggle_user_state, name='admin_toggle_user_state'),
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
