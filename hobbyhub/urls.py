"""
Main URL configuration for the HobbyHub project.

Includes app-level URLconfs for:
- home (landing and static pages)
- boxes (past box listings and details)
- users (registration, login, account management)
- orders (order history and Stripe hooks)
- dashboard (custom admin views)

Admin interface also mounted at /admin/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Routes root URL to the home app
    path('past_boxes/', include('boxes.urls')),  # Routes root URL to the boxes app
    path('accounts/', include('users.urls')), # Routes to user based URLs in the users app
    path('orders/', include('orders.urls')), # Routes to order based URLs in the orders app
    path('dashboard/', include('dashboard.urls')), # Routes to custom admin UI
    ]
