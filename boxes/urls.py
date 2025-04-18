"""
# boxes/urls.py
Defines URL patterns for the boxes app.
Includes views for listing past boxes and viewing individual box details.
"""

from django.urls import path
from . import views

# URL patterns for box-related views within the boxes app
urlpatterns = [
    path('past_boxes/', views.past_boxes, name='past_boxes'),
    path('past_boxes/<slug:slug>/', views.box_detail, name='box_detail'),
]
