# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('past_boxes/', views.past_boxes, name='past_boxes'),
    path('past_boxes/<slug:slug>/', views.box_detail, name='box_detail'),
]
