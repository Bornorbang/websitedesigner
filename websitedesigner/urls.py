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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticSitemap, BlogSitemap, CategorySitemap
from app.views import *

sitemaps = {
    'static': StaticSitemap,
    'blogs': BlogSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Add this line to redirect to the home view.
    path('about-website-designer-nigeria/', about, name= 'about-website-designer-nigeria'),
    path('website-development-services/', services, name= 'services'),
    path('categories/<slug:category_slug>/', category_posts, name='category_posts'),
    path('contact-website-designer-nigeria/', contact, name= 'contact'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('<slug:category_slug>/<slug:slug>/', blog_detail, name='blog_detail'),
    path('blog/', blog_list, name='blogs'),
    path('website-designer-in-lagos/', website_lagos, name="website_lagos"),
    path('seo-company-in-nigeria', seo_company, name="seo_services"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
