"""hobbyhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
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
