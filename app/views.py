from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import logging
# Create your views here.

def home(request):
    recent_blogs = Blog.objects.order_by('-date')[:2]
    return render(request, 'index.html', {'recent_blogs': recent_blogs})

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Send email
        subject = f"New contact form submission from {name}"
        email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        from_email = "contact@websitedesigner.ng"
        recipient_list = [settings.CONTACT_EMAIL]  # You need to define this in settings.py

        try:
            send_mail(subject, email_message, from_email, recipient_list)
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
        except Exception as e:
            messages.error(request, {e})

        return redirect('contact')

    return render(request, 'contact.html')

def blog_detail(request, category_slug, slug):
    # Get the category object using the category slug
    category = get_object_or_404(Category, slug=category_slug)

    # Get the blog post using the category and blog slug
    blog = get_object_or_404(Blog, category=category, slug=slug)

    # Fetch the 5 most recent posts
    recent_posts = Blog.objects.all()[:5]  # The ordering is now handled by the model

    # Get all categories
    categories = Category.objects.all()

    banners = BlogSidebarBanner.objects.all()[:3] 

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'recent_posts': recent_posts,
        'categories': categories,
        'category': category,
        'banners': banners,
    })

def blog_list(request):
    blogs = Blog.objects.all()
    paginator = Paginator(blogs, 10)  # Show 10 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    banners = BlogslistSidebarBanner.objects.all()[:3] 
    return render(request, 'blogs.html', {'page_obj': page_obj, 'banners': banners})

def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = category.blogs.all()  # The ordering is now handled by the model
    paginator = Paginator(posts, 5)  # Paginate with 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Dynamic sidebar data
    categories = Category.objects.all()
    recent_posts = Blog.objects.all()[:5]  # The ordering is now handled by the model
    banners = BlogSidebarBanner.objects.all()

    return render(request, 'category_list.html', {
        'category': category,
        'page_obj': page_obj,
        'categories': categories,
        'recent_posts': recent_posts,
        'banners': banners,
    })

def website_lagos(request):
    return render(request, 'website_lagos.html')


def seo_services(request):
    return render(request, 'seo_services.html')