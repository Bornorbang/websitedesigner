from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import logging
from django.db.models import Q
# Create your views here.

def home(request):
    recent_blogs = Blog.objects.exclude(category__slug__in=['tech-reviews', 'tech-tips']).order_by('-date')[:2]
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

        subject = f"New contact form submission from {name}"
        email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        from_email = "contact@websitedesigner.ng"
        recipient_list = [settings.CONTACT_EMAIL]

        try:
            send_mail(subject, email_message, from_email, recipient_list)
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
        except Exception as e:
            messages.error(request, {e})

        return redirect('contact')

    return render(request, 'contact.html')

def blog_detail(request, category_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    blog = get_object_or_404(Blog, category=category, slug=slug)
    recent_posts = Blog.objects.all()[:5]
    related_posts = Blog.objects.filter(Q(category=blog.category) & ~Q(id=blog.id)).order_by('-date')[:3]
    categories = Category.objects.all()
    banners = BlogSidebarBanner.objects.all()[:3]
    
    comments = blog.comments.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('comment')
        
        if name and email and content:
            Comment.objects.create(blog=blog, name=name, email=email, content=content)
            messages.success(request, 'Your comment has been posted successfully.')
            return redirect('blog_detail', category_slug=category_slug, slug=slug)
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'recent_posts': recent_posts,
        'categories': categories,
        'category': category,
        'banners': banners,
        'related_posts': related_posts,
        'comments': comments,
    })

def blog_list(request):
    # Exclude "Reviews" and "Tech Tips" categories from the main blog list
    blogs = Blog.objects.exclude(category__slug__in=['tech-reviews', 'tech-tips'])
    paginator = Paginator(blogs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    banners = BlogslistSidebarBanner.objects.all()[:3]
    return render(request, 'blogs.html', {'page_obj': page_obj, 'banners': banners})

def reviews(request):
    # Fetch only posts in the "Reviews" category
    reviews_category = get_object_or_404(Category, slug='tech-reviews')
    reviews_posts = Blog.objects.filter(category=reviews_category)
    paginator = Paginator(reviews_posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'reviews.html', {'page_obj': page_obj, 'category': reviews_category})

def tech_tips(request):
    # Fetch only posts in the "Tech Tips" category
    tech_tips_category = get_object_or_404(Category, slug='tech-tips')
    tech_tips_posts = Blog.objects.filter(category=tech_tips_category)
    paginator = Paginator(tech_tips_posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'tech_tips.html', {'page_obj': page_obj, 'category': tech_tips_category})

def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = category.blogs.all() 
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Dynamic sidebar data
    categories = Category.objects.all()
    recent_posts = Blog.objects.all()[:5] 
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


def seo_company(request):
    return render(request, 'seo_company.html')


def graphic_design(request):
    return render(request, 'graphic_design.html')

def consultation(request):
    return render(request, 'consultation.html')

def pricing(request):
    return render(request, 'pricing.html')

def advertise(request):
    return render(request, 'advertise.html')

def courses(request):
    return render(request, 'courses.html')

def ecommerce(request):
    return render(request, 'ecommerce.html')

def seo_pricing(request):
    return render(request, 'seo_pricing.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')


























