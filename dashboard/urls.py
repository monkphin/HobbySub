# dashboard/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('box_admin/', views.box_admin, name='box_admin'),
    path('add_box/', views.add_box, name='add_box'),
    path('box_admin/<int:box_id>/edit/', views.edit_box, name='edit_box'),
    path('box_admin/<int:box_id>/delete/', views.delete_box, name='delete_box'),
]