# dashboard/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('box_admin/', views.box_admin, name='box_admin'),
    path('add_box/', views.add_box, name='add_box'),
    path('box_admin/<int:box_id>/edit/', views.edit_box, name='edit_box'),
    path('box_admin/<int:box_id>/delete/', views.delete_box, name='delete_box'),
    path('products/add/', views.add_products, name='add_products'),
    path('box_admin/<int:box_id>/products/', views.edit_box_products, name='edit_box_products'),
    path('box_admin/<int:box_id>/products/add/', views.add_product_to_box, name='add_product_to_box'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/<int:product_id>/remove/', views.remove_product_from_box, name='remove_product_from_box'),
]