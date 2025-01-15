"""
URL configuration for websitedesigner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from app.views import home, about, services, contact
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticSitemap  # Import your StaticSitemap

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Add this line to redirect to the home view.
    path('about-website-designer-nigeria/', about, name= 'about-website-designer-nigeria'),
    path('website-development-services/', services, name= 'services'),
    path('contact-website-designer-nigeria/', contact, name= 'contact'),
    path('sitemap.xml', sitemap, {'sitemaps': {'static': StaticSitemap}}),
]
