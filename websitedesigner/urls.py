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
    path('', home, name='home'),  
    path('about-website-designer-nigeria/', about, name= 'about-website-designer-nigeria'),
    path('website-development-services/', services, name= 'services'),
    path('categories/<slug:category_slug>/', category_posts, name='category_posts'),
    path('contact-website-designer-nigeria/', contact, name= 'contact'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('course/<slug:slug>/', course_detail, name="course_detail"),
    path('tech-blog/', blog_list, name='blogs'),
    path('web-designer-in-lagos/', website_lagos, name="website_lagos"),
    path('seo-company-in-nigeria', seo_company, name="seo_services"),
    path('best-graphic-designer-nigeria/', graphic_design, name="graphic_design"),
    path('tech-tips/', tech_tips, name="tech_tips"),
    path('tech-reviews/', reviews, name="tech_reviews"),
    path('advertise-with-us/', advertise, name="advertise"),
    path('earn-money/', earn_money, name="earn_money"),
    path('consultation/', consultation, name="consultation"),
    path('book-consultation/', consultation_booking, name="consultation_booking"),
    path('web-development-pricing/', pricing, name="pricing"),
    path('shopify-store-pricing/', shopify_pricing, name="shopify_pricing"),
    path('tech-courses/', courses, name="courses"),
    path('courses/<slug:slug>/', course_category, name="course_category"),
    path('seo-pricing/', seo_pricing, name="seo_pricing"),
    path('terms-of-service/', terms, name="terms"),
    path('privacy-policy/', privacy, name="privacy"),
    path('ecommerce-website-design-in-nigeria/', ecommerce, name="ecommerce"),
    path('portfolio/', portfolio, name="portfolio"),
    path('20-days-with-wdn/', twenty_days_workshop, name="twenty_days_workshop"),
    
    # Authentication URLs
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('check-email/', check_email_exists, name='check_email'),
    path('check-username/', check_username_exists, name='check_username'),
    path('remove-profile-image/', remove_profile_image, name='remove_profile_image'),
    
    # Course URLs
    path('course/<int:course_id>/review/', submit_review, name='submit_review'),
    path('course/<int:course_id>/enroll/', enroll_course, name='enroll_course'),
    path('course/<int:course_id>/checkout/', direct_course_checkout, name='direct_course_checkout'),
    path('review/<int:review_id>/like/', like_review, name='like_review'),
    
    # Payment URLs
    path('payment/course/<int:course_id>/', initiate_course_payment, name='initiate_course_payment'),
    path('payment/process/', process_course_payment, name='process_course_payment'),
    path('payment/verify/', verify_payment, name='verify_payment'),
    path('payment/webhook/', paystack_webhook, name='paystack_webhook'),
    path('payment/webhook/', kora_pay_webhook, name='kora_pay_webhook'),  # Backward compatibility
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/failed/', payment_failed, name='payment_failed'),
    
    # Consultation Payment URLs
    path('consultation/payment/process/', process_consultation_payment, name='process_consultation_payment'),
    path('verify-consultation-payment/<str:reference>/', verify_consultation_payment, name='verify_consultation_payment'),
    
    # Lecture URLs
    path('course/<slug:course_slug>/lecture/<int:lecture_id>/', lecture_detail, name='lecture_detail'),
    path('lecture/<int:lecture_id>/download/', download_attachment, name='download_attachment'),
    path('lecture/<int:lecture_id>/resources/', lecture_resources, name='lecture_resources'),
    
    # Affiliate URLs - MUST be before blog catch-all
    path('affiliate/dashboard/', affiliate_dashboard, name='affiliate_dashboard'),
    path('affiliate/join/', become_affiliate, name='become_affiliate'),
    path('affiliate/payout/', request_payout, name='request_payout'),
    
    # Authentication URLs - MUST be before blog catch-all
    path('accounts/login/', login_view, name='account_login'),
    path('accounts/signup/', signup_view, name='account_signup'),
    path('accounts/logout/', logout_view, name='account_logout'),
    
    # Blog URLs - MUST BE LAST because it's a catch-all pattern
    path('<slug:category_slug>/<slug:slug>/', blog_detail, name='blog_detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
