from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import logging
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CourseReviewForm
from django.http import JsonResponse
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
    # Get published courses from database
    published_courses = Course.objects.filter(status='published').order_by('-created_at')
    
    context = {
        'published_courses': published_courses,
    }
    return render(request, 'courses.html', context)

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Get related courses (same category)
    related_courses = Course.objects.filter(
        category=course.category, 
        status='published'
    ).exclude(id=course.id)[:4]
    
    # Get course sections with lectures
    sections = course.sections.all().prefetch_related('lectures')
    
    # Get reviews with helpful status
    reviews = course.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Add helpful status for authenticated users
    for review in reviews:
        if request.user.is_authenticated:
            review.user_found_helpful = review.is_helpful_by_user(request.user)
        else:
            review.user_found_helpful = False
    
    # Check user enrollment and review status
    user_enrolled = False
    can_review = False
    user_review = None
    review_form = None
    
    if request.user.is_authenticated:
        # Auto-enroll logged-in users
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'is_paid': True}  # Mark as paid for free access
        )
        
        user_enrolled = True  # Always true since we auto-enroll
        can_review = course.can_user_review(request.user)
        user_review = course.get_user_review(request.user)
        
        if can_review:
            review_form = CourseReviewForm()
    
    context = {
        'course': course,
        'related_courses': related_courses,
        'sections': sections,
        'reviews': reviews,
        'user_enrolled': user_enrolled,
        'can_review': can_review,
        'user_review': user_review,
        'review_form': review_form,
    }
    return render(request, 'course_detail.html', context)

def ecommerce(request):
    return render(request, 'ecommerce.html')

def seo_pricing(request):
    return render(request, 'seo_pricing.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def consultation_booking(request):
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company', '')
        industry = request.POST.get('industry', '')
        project_type = request.POST.get('projectType')
        budget = request.POST.get('budget', '')
        timeline = request.POST.get('timeline', '')
        consultation_type = request.POST.get('consultationType')
        preferred_date = request.POST.get('preferredDate', '')
        preferred_time = request.POST.get('preferredTime', '')
        project_description = request.POST.get('projectDescription', '')
        current_website = request.POST.get('currentWebsite', '')
        inspiration = request.POST.get('inspiration', '')
        additional_services = request.POST.getlist('additionalServices')
        
        # Format additional services
        services_text = ', '.join(additional_services) if additional_services else ''
        
        # Save to database
        try:
            consultation = ConsultationBooking.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                industry=industry,
                project_type=project_type,
                budget=budget,
                timeline=timeline,
                consultation_type=consultation_type,
                preferred_date=preferred_date if preferred_date else None,
                preferred_time=preferred_time,
                project_description=project_description,
                current_website=current_website,
                inspiration=inspiration,
                additional_services=services_text,
            )
            
            # Create email content
            subject = f"New Consultation Request from {first_name} {last_name} (ID: {consultation.id})"
            
            email_message = f"""
New consultation booking received!

CONSULTATION ID: {consultation.id}
BOOKING DATE: {consultation.created_at.strftime('%Y-%m-%d %H:%M:%S')}

PERSONAL INFORMATION:
Name: {first_name} {last_name}
Email: {email}
Phone: {phone}
Company: {company if company else 'Not provided'}
Industry: {industry if industry else 'Not provided'}

PROJECT DETAILS:
Project Type: {project_type}
Budget Range: {budget if budget else 'Not specified'}
Timeline: {timeline if timeline else 'Not specified'}
Description: {project_description if project_description else 'Not provided'}
Current Website: {current_website if current_website else 'None'}
Inspiration/References: {inspiration if inspiration else 'None'}

CONSULTATION PREFERENCES:
Consultation Type: {consultation_type}
Preferred Date: {preferred_date if preferred_date else 'Not specified'}
Preferred Time: {preferred_time if preferred_time else 'Not specified'}

ADDITIONAL SERVICES:
{services_text if services_text else 'None'}

---
This consultation request was submitted via the Website Designer Nigeria consultation form.
Please respond within 24 hours as promised to the client.

View in Admin: http://yourwebsite.com/admin/app/consultationbooking/{consultation.id}/
            """
            
            # Email to admin
            send_mail(
                subject,
                email_message,
                "consultation@websitedesigner.ng",
                ["admin@websitedesigner.ng", "info@websitedesigner.ng"],
                fail_silently=False,
            )
            
            # Confirmation email to client
            client_subject = "Your Consultation Request - Website Designer Nigeria"
            client_message = f"""
Dear {first_name},

Thank you for booking a consultation with Website Designer Nigeria!

We've received your consultation request for your {project_type} project and are excited to discuss how we can help bring your vision to life.

CONSULTATION REFERENCE: #{consultation.id}

WHAT HAPPENS NEXT:
• Our team will review your project details
• We'll contact you within 24 hours to confirm your consultation appointment
• You'll receive a calendar invite for the scheduled time
• We'll prepare a custom discussion agenda based on your requirements

YOUR CONSULTATION DETAILS:
• Consultation Type: {consultation_type}
• Preferred Date: {preferred_date if preferred_date else 'To be confirmed'}
• Preferred Time: {preferred_time if preferred_time else 'To be confirmed'}

CONSULTATION FEES:
Please note that consultation fees may apply based on the scope and complexity of your project. Our team will discuss this with you during the scheduling call.

If you have any urgent questions before our call, feel free to reach out to us at:
• WhatsApp: https://wa.link/f2kd41
• Email: info@websitedesigner.ng
• Phone: +234 XXX XXX XXXX

We're looking forward to our conversation!

Best regards,
The Website Designer Nigeria Team
www.websitedesigner.ng
            """
            
            send_mail(
                client_subject,
                client_message,
                "consultation@websitedesigner.ng",
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Your consultation has been booked successfully! We will contact you within 24 hours.')
            return redirect('consultation_booking')
            
        except Exception as e:
            messages.error(request, 'There was an error processing your request. Please try again or contact us directly.')
            logging.error(f"Consultation booking error: {e}")
    
    return render(request, 'consultation_booking.html')


# Authentication Views
def signup_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after signup
            login(request, user)
            messages.success(request, f'Welcome to Website Designer Nigeria, {user.get_full_name() or user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with email first, then username
            user = None
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('profile')
            else:
                messages.error(request, 'Invalid email/username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = UserProfileForm(instance=profile, user=request.user)
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': user_form,
        'profile': profile
    })


@login_required
def check_email_exists(request):
    """AJAX view to check if email already exists"""
    email = request.GET.get('email')
    user_id = request.GET.get('user_id')  # Current user ID for profile updates
    
    exists = User.objects.filter(email=email).exists()
    
    # If updating profile, exclude current user
    if user_id:
        exists = User.objects.filter(email=email).exclude(id=user_id).exists()
    
    return JsonResponse({'exists': exists})


def check_username_exists(request):
    """AJAX view to check if username already exists"""
    username = request.GET.get('username')
    user_id = request.GET.get('user_id')  # Current user ID for profile updates
    
    exists = User.objects.filter(username=username).exists()
    
    # If updating profile, exclude current user
    if user_id:
        exists = User.objects.filter(username=username).exclude(id=user_id).exists()
    
    return JsonResponse({'exists': exists})


@login_required
def remove_profile_image(request):
    """AJAX view to remove user's profile image"""
    if request.method == 'POST':
        try:
            profile = request.user.profile
            if profile.profile_image:
                # Delete the file from storage
                profile.profile_image.delete()
                profile.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'No profile image to remove'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def submit_review(request, course_id):
    """Handle course review submission"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Check if user can review this course
    if not course.can_user_review(request.user):
        return JsonResponse({
            'success': False, 
            'error': 'You must be enrolled in this course to leave a review and can only review once.'
        })
    
    if request.method == 'POST':
        form = CourseReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.course = course
            review.save()
            
            # Update course rating
            course.update_rating_from_reviews()
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your review!',
                'review': {
                    'rating': review.rating,
                    'review_text': review.review_text,
                    'student_name': review.student_name,
                    'created_at': review.created_at.strftime('%b %d, %Y')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def like_review(request, review_id):
    """Handle review helpful vote"""
    if request.method == 'POST':
        try:
            review = get_object_or_404(CourseReview, id=review_id)
            is_helpful = review.toggle_helpful(request.user)
            
            message = 'Marked as helpful!' if is_helpful else 'Removed helpful mark'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'helpful_count': review.helpful_count,
                'is_helpful': is_helpful
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to record your feedback.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def enroll_course(request, course_id):
    """Handle course enrollment"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    if request.method == 'POST':
        # Check if already enrolled
        if course.is_enrolled_by_user(request.user):
            return JsonResponse({
                'success': False,
                'error': 'You are already enrolled in this course.'
            })
        
        # Create enrollment
        from .models import CourseEnrollment
        enrollment = CourseEnrollment.objects.create(
            user=request.user,
            course=course,
            is_paid=course.is_free  # For free courses, mark as paid immediately
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully enrolled in {course.title}!',
            'is_free': course.is_free
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def lecture_detail(request, course_slug, lecture_id):
    """
    Display individual lecture content with access control
    """
    course = get_object_or_404(Course, slug=course_slug)
    lecture = get_object_or_404(Lecture, id=lecture_id, section__course=course)
    
    # Check if user has access to this lecture
    user_enrolled = False
    if request.user.is_authenticated:
        # Auto-enroll logged-in users
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'is_paid': True}  # Mark as paid for free access
        )
        user_enrolled = True
    
    # Access control
    has_access = lecture.is_preview or user_enrolled or (request.user.is_authenticated and request.user.is_staff)
    
    if not has_access:
        messages.error(request, 'You need to enroll in this course to access this lecture.')
        return redirect('course_detail', slug=course_slug)
    
    # Get neighboring lectures for navigation
    all_lectures = []
    for section in course.sections.all():
        all_lectures.extend(section.lectures.all())
    
    current_index = None
    for i, lec in enumerate(all_lectures):
        if lec.id == lecture.id:
            current_index = i
            break
    
    prev_lecture = all_lectures[current_index - 1] if current_index and current_index > 0 else None
    next_lecture = all_lectures[current_index + 1] if current_index is not None and current_index < len(all_lectures) - 1 else None
    
    context = {
        'course': course,
        'lecture': lecture,
        'user_enrolled': user_enrolled,
        'has_access': has_access,
        'prev_lecture': prev_lecture,
        'next_lecture': next_lecture,
        'lecture_number': current_index + 1 if current_index is not None else 1,
        'total_lectures': len(all_lectures)
    }
    
    return render(request, 'lecture_detail.html', context)


def download_attachment(request, lecture_id):
    """
    Handle lecture attachment downloads with access control
    """
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.section.course
    
    # Check access
    user_enrolled = False
    if request.user.is_authenticated:
        # Auto-enroll logged-in users
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'is_paid': True}  # Mark as paid for free access
        )
        user_enrolled = True
    
    has_access = lecture.is_preview or user_enrolled or (request.user.is_authenticated and request.user.is_staff)
    
    if not has_access:
        messages.error(request, 'You need to enroll in this course to download attachments.')
        return redirect('course_detail', slug=course.slug)
    
    if not lecture.attachments:
        messages.error(request, 'No attachment available for this lecture.')
        return redirect('lecture_detail', course_slug=course.slug, lecture_id=lecture.id)
    
    # Serve the file
    from django.http import HttpResponse, Http404
    import os
    import mimetypes
    
    file_path = lecture.attachments.path
    if os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(
            lecture.attachments.read(),
            content_type=mime_type or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    else:
        raise Http404("File not found")


def lecture_resources(request, lecture_id):
    """
    Return lecture resources (content and attachments) as JSON
    """
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.section.course
    
    # Auto-enroll authenticated users
    user_enrolled = False
    if request.user.is_authenticated:
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'is_paid': True}
        )
        user_enrolled = True
    
    has_access = lecture.is_preview or user_enrolled or (request.user.is_authenticated and request.user.is_staff)
    
    if not has_access:
        return JsonResponse({
            'success': False,
            'error': 'You need to enroll in this course to access lecture resources.'
        })
    
    resources = {
        'attachments': [],
        'content': None
    }
    
    # Add attachment if exists
    if lecture.attachments:
        import os
        resources['attachments'].append({
            'name': os.path.basename(lecture.attachments.name),
            'url': f'/lecture/{lecture.id}/download/',
            'size': lecture.attachments.size if hasattr(lecture.attachments, 'size') else None
        })
    
    # Add rich text content if exists
    if lecture.content:
        resources['content'] = lecture.content
    
    return JsonResponse({
        'success': True,
        'resources': resources
    })
