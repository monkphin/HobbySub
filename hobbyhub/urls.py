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
from django.contrib.sitemaps.views import sitemap
from home.sitemaps import StaticViewSitemap, BoxSitemap
from allauth.account.views import LogoutView
from django.urls import path, include
from django.views.static import serve
from django.contrib import admin
from django.conf import settings
from django.urls import re_path



sitemaps = {
            'static': StaticViewSitemap,
            'boxes': BoxSitemap,
            }


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('past_boxes/', include('boxes.urls')),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    re_path(r'^robots\.txt$', serve, {
        'path': 'robots.txt',
        'document_root': settings.STATIC_ROOT,
    }),
    ]
