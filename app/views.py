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
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
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
    
    # Check user enrollment and payment status
    user_enrolled = False
    can_review = False
    user_review = None
    review_form = None
    enrollment_status = None
    has_pending_payment = False
    
    if request.user.is_authenticated:
        # Check if user is enrolled (paid)
        user_enrolled = course.is_enrolled_by_user(request.user)
        
        # Check for pending payments
        has_pending_payment = course.has_pending_payment(request.user)
        
        # Get enrollment status
        enrollment = course.get_user_enrollment(request.user)
        if enrollment:
            enrollment_status = enrollment.status
        
        # For free courses, auto-enroll if not already enrolled
        if course.is_free and not user_enrolled and not has_pending_payment:
            enrollment, created = CourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 'enrolled',
                    'is_paid': True  # Free courses are considered "paid"
                }
            )
            user_enrolled = True
            enrollment_status = 'enrolled'
        
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
        'enrollment_status': enrollment_status,
        'has_pending_payment': has_pending_payment,
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
    # Check for payment success parameter
    if request.GET.get('payment') == 'success':
        reference = request.GET.get('reference')
        if reference:
            # Auto-verify the payment if reference is provided
            return verify_consultation_payment(request, reference)
        # If no reference, just show success message
        messages.success(request, 'Payment successful! We will contact you within 24 hours to confirm your appointment.')
    
    if request.method == 'POST':
        # All form submissions now go through payment processing
        return process_consultation_payment(request)
    
    return render(request, 'consultation_booking.html')

def process_consultation_payment(request):
    """Process consultation payment via Kora Pay"""
    if request.method == 'POST':
        try:
            # Extract form data
            full_name = request.POST.get('fullName')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            consultation_type = request.POST.get('consultationType')
            preferred_date = request.POST.get('preferredDate', '')
            preferred_time = request.POST.get('preferredTime', '')
            project_description = request.POST.get('projectDescription', '')
            inspiration = request.POST.get('inspiration', '')
            session_duration = request.POST.get('sessionDuration', '')
            consultation_cost = request.POST.get('consultationCost', '')
            
            # Validate required fields
            if not all([full_name, email, phone, consultation_type, session_duration, consultation_cost]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('consultation_booking')
            
            # Parse consultation cost (remove commas)
            try:
                amount = float(consultation_cost.replace(',', ''))
            except ValueError:
                messages.error(request, 'Invalid consultation cost.')
                return redirect('consultation_booking')
            
            # Split full name into first and last name for model compatibility
            name_parts = full_name.strip().split(' ', 1) if full_name else ['', '']
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Create consultation booking first
            consultation = ConsultationBooking.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company='',
                industry='',
                project_type='consultation',
                budget='',
                timeline='',
                consultation_type=consultation_type,
                preferred_date=preferred_date if preferred_date else None,
                preferred_time=preferred_time,
                session_duration=session_duration,
                consultation_cost=consultation_cost,
                project_description=project_description,
                current_website='',
                inspiration=inspiration,
                additional_services='',
                status='pending'  # Will be updated when payment is completed
            )
            
            # Generate unique transaction reference
            import uuid
            transaction_id = f"CONS_{consultation.id}_{uuid.uuid4().hex[:8].upper()}"
            reference = f"consultation_{consultation.id}_{uuid.uuid4().hex[:12]}"
            
            # Create consultation payment record
            from .models import ConsultationPayment
            payment = ConsultationPayment.objects.create(
                consultation_booking=consultation,
                amount=amount,
                currency='NGN',
                payment_method='kora_pay',
                status='pending',
                transaction_id=transaction_id,
                reference=reference
            )
            
            # Initialize payment with Kora Pay
            import requests
            from django.conf import settings
            
            kora_pay_data = {
                "amount": int(amount),  # Amount in naira (not kobo)
                "currency": "NGN",
                "reference": reference,
                "redirect_url": request.build_absolute_uri("/book-consultation/?payment=success"),
                "notification_url": request.build_absolute_uri(f"/verify-consultation-payment/{reference}/"),
                "narration": f"Consultation booking payment - {session_duration} minutes",
                "channels": ["card", "bank_transfer", "pay_with_bank"],
                "customer": {
                    "email": email,
                    "name": full_name
                },
                "metadata": {
                    "consultation_id": str(consultation.id),
                    "payment_id": str(payment.id),
                    "session_duration": session_duration,
                    "phone": phone
                }
            }
            
            headers = {
                "Authorization": f"Bearer {settings.KORA_PAY_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            # Debug logging
            print(f"Kora Pay API URL: {settings.KORA_PAY_BASE_URL}/charges/initialize")
            print(f"Headers: {headers}")
            print(f"Request data: {kora_pay_data}")
            
            response = requests.post(
                f"{settings.KORA_PAY_BASE_URL}/charges/initialize",
                json=kora_pay_data,
                headers=headers,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('status') and response_data.get('data'):
                    checkout_url = response_data['data'].get('checkout_url')
                    
                    # Store payment details
                    payment.payment_details = response_data['data']
                    payment.external_transaction_id = response_data['data'].get('reference', reference)
                    payment.save()
                    
                    return redirect(checkout_url)
                else:
                    payment.mark_as_failed('Invalid response from payment gateway')
                    messages.error(request, 'Payment initialization failed. Please try again.')
                    return redirect('consultation_booking')
            else:
                payment.mark_as_failed(f'Payment gateway error: {response.status_code}')
                messages.error(request, 'Payment service unavailable. Please try again later.')
                return redirect('consultation_booking')
                
        except Exception as e:
            logging.error(f"Consultation payment error: {e}")
            messages.error(request, 'An error occurred while processing your payment. Please try again.')
            return redirect('consultation_booking')
    
    return redirect('consultation_booking')


def verify_consultation_payment(request, reference):
    """Verify consultation payment from Kora Pay"""
    try:
        from .models import ConsultationPayment
        payment = ConsultationPayment.objects.get(reference=reference)
        
        # Verify payment with Kora Pay
        import requests
        from django.conf import settings
        
        headers = {
            "Authorization": f"Bearer {settings.KORA_PAY_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{settings.KORA_PAY_BASE_URL}/charges/{reference}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('status') and response_data.get('data'):
                transaction_data = response_data['data']
                transaction_status = transaction_data.get('status', '').lower()
                
                if transaction_status == 'success':
                    # Mark payment as completed
                    payment.external_transaction_id = transaction_data.get('payment_reference', reference)
                    payment.payment_details.update(transaction_data)
                    payment.mark_as_completed()
                    
                    # Update consultation booking status to confirmed
                    consultation = payment.consultation_booking
                    consultation.status = 'confirmed'
                    consultation.save()
                    
                    # Send confirmation emails (reuse existing email logic)
                    from django.core.mail import send_mail
                
                # Admin email
                admin_subject = f"New Paid Consultation Request from {consultation.full_name} (ID: {consultation.id})"
                admin_message = f"""
Paid consultation booking received!

CONSULTATION ID: {consultation.id}
PAYMENT ID: {payment.id}
BOOKING DATE: {consultation.created_at.strftime('%Y-%m-%d %H:%M:%S')}
PAYMENT STATUS: PAID

PERSONAL INFORMATION:
Name: {consultation.full_name}
Email: {consultation.email}
Phone: {consultation.phone}

CONSULTATION DETAILS:
Consultation Type: {consultation.consultation_type}
Session Duration: {consultation.session_duration} minutes
Amount Paid: ₦{payment.amount}
Preferred Date: {consultation.preferred_date if consultation.preferred_date else 'Not specified'}
Preferred Time: {consultation.preferred_time if consultation.preferred_time else 'Not specified'}

PROJECT DETAILS:
Description: {consultation.project_description if consultation.project_description else 'Not provided'}
Inspiration/References: {consultation.inspiration if consultation.inspiration else 'None'}

PAYMENT DETAILS:
Transaction ID: {payment.transaction_id}
Reference: {payment.reference}
Payment Method: KoraPay

---
This is a PAID consultation request. Please prioritize and respond within 24 hours.

View in Admin: http://yourwebsite.com/admin/app/consultationbooking/{consultation.id}/
"""
                
                send_mail(
                    admin_subject,
                    admin_message,
                    "consultation@websitedesigner.ng",
                    [settings.CONTACT_EMAIL],
                    fail_silently=True,
                )
                
                # Client confirmation email
                client_subject = "Payment Confirmed - Your Consultation is Booked!"
                client_message = f"""
Dear {consultation.first_name},

Great news! Your payment has been confirmed and your consultation is now booked.

PAYMENT CONFIRMATION:
✅ Amount Paid: ₦{payment.amount}
✅ Transaction ID: {payment.transaction_id}
✅ Payment Date: {payment.paid_at.strftime('%Y-%m-%d %H:%M:%S')}

YOUR CONSULTATION DETAILS:
• Session Duration: {consultation.session_duration} minutes
• Consultation Type: {consultation.consultation_type}
• Preferred Date: {consultation.preferred_date if consultation.preferred_date else 'To be confirmed'}
• Preferred Time: {consultation.preferred_time if consultation.preferred_time else 'To be confirmed'}

WHAT HAPPENS NEXT:
• Our team will contact you within 24 hours to confirm your appointment
• You'll receive a calendar invite for the scheduled time
• We'll prepare a custom discussion agenda based on your requirements

If you have any questions, please contact us at:
• WhatsApp: https://wa.link/f2kd41
• Email: info@websitedesigner.ng

Thank you for choosing Website Designer Nigeria!

Best regards,
The Website Designer Nigeria Team
www.websitedesigner.ng
"""
                
                send_mail(
                    client_subject,
                    client_message,
                    "consultation@websitedesigner.ng",
                    [consultation.email],
                    fail_silently=True,
                )
                
                messages.success(request, 'Payment successful! We will contact you within 24 hours to confirm your appointment.')
                return redirect('consultation_booking')
                
            elif transaction_status == 'failed':
                payment.mark_as_failed('Payment failed at gateway')
                messages.error(request, 'Payment failed. Please try again.')
                return redirect('consultation_booking')
                
            elif transaction_status == 'pending':
                messages.info(request, 'Payment is still being processed. Please check back shortly.')
                return redirect('consultation_booking')
                
            elif transaction_status == 'processing':
                messages.info(request, 'Payment is being processed. Please check back in a few minutes.')
                return redirect('consultation_booking')
                
            elif transaction_status in ['cancelled', 'abandoned']:
                payment.mark_as_failed('Payment cancelled by user')
                messages.warning(request, 'Payment was cancelled. You can try again to complete your consultation booking.')
                return redirect('consultation_booking')
                
            else:
                messages.info(request, f'Payment status: {transaction_status}. Please contact support if you need assistance.')
                return redirect('consultation_booking')
        else:
            messages.error(request, 'Unable to verify payment status. Please contact support with your payment reference.')
            return redirect('consultation_booking')
            
    except ConsultationPayment.DoesNotExist:
        messages.error(request, 'Payment record not found')
        return redirect('consultation_booking')
    except Exception as e:
        logging.error(f"Consultation payment verification error: {e}")
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('consultation_booking')


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
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Check for direct course purchase flow
            course_id = request.POST.get('course_id') or request.GET.get('course_id')
            next_url = request.POST.get('next') or request.GET.get('next')
            
            if course_id:
                try:
                    course = Course.objects.get(id=course_id, status='published')
                    
                    # For free courses, enroll directly
                    if course.is_free:
                        enrollment = CourseEnrollment.objects.create(
                            user=user,
                            course=course,
                            status='enrolled',
                            is_paid=True
                        )
                        messages.success(request, f'Welcome to Website Designer Nigeria, {user.get_full_name() or user.username}! You have been enrolled in {course.title}!')
                        return redirect(course.get_absolute_url())
                    
                    # For paid courses, redirect to direct checkout (don't show welcome message yet)
                    return redirect('direct_course_checkout', course_id=course.id)
                    
                except Course.DoesNotExist:
                    messages.error(request, 'Course not found.')
            
            # Show welcome message for regular signup (non-course)
            messages.success(request, f'Welcome to Website Designer Nigeria, {user.get_full_name() or user.username}!')
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
                login(request, user, backend='app.backends.EmailOrUsernameModelBackend')
                
                # Check for direct course purchase flow
                course_id = request.POST.get('course_id') or request.GET.get('course_id')
                next_url = request.POST.get('next') or request.GET.get('next')
                
                if course_id:
                    try:
                        course = Course.objects.get(id=course_id, status='published')
                        
                        # For free courses, enroll directly
                        if course.is_free:
                            enrollment, created = CourseEnrollment.objects.get_or_create(
                                user=user,
                                course=course,
                                defaults={
                                    'status': 'enrolled',
                                    'is_paid': True
                                }
                            )
                            if created:
                                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}! You have been enrolled in {course.title}!')
                            else:
                                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                            return redirect(course.get_absolute_url())
                        
                        # For paid courses, redirect to direct checkout (don't show welcome message yet)
                        return redirect('direct_course_checkout', course_id=course.id)
                        
                    except Course.DoesNotExist:
                        messages.error(request, 'Course not found.')
                
                # Show welcome message for regular login (non-course)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
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
    """Handle course enrollment/payment initiation"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Please login to enroll in courses.',
            'redirect': '/login/'
        })
    
    if request.method == 'POST':
        # Check if already enrolled
        if course.is_enrolled_by_user(request.user):
            return JsonResponse({
                'success': False,
                'error': 'You are already enrolled in this course.'
            })
        
        # Check if has pending payment
        if course.has_pending_payment(request.user):
            return JsonResponse({
                'success': False,
                'error': 'You already have a pending payment for this course.'
            })
        
        # Handle free courses
        if course.is_free:
            enrollment = CourseEnrollment.objects.create(
                user=request.user,
                course=course,
                status='enrolled',
                is_paid=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully enrolled in {course.title}!',
                'is_free': True,
                'redirect': course.get_absolute_url()
            })
        
        # Handle paid courses - get or create pending enrollment and redirect to payment
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'status': 'pending',
                'is_paid': False
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Please complete payment to enroll.',
            'is_free': False,
            'payment_url': f'/payment/course/{course.id}/',
            'redirect': f'/payment/course/{course.id}/'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def direct_course_checkout(request, course_id):
    """Direct course checkout for new users after signup"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Check if course is free
    if course.is_free:
        messages.error(request, 'This course is free. No payment required.')
        return redirect(course.get_absolute_url())
    
    # Check if already enrolled
    if course.is_enrolled_by_user(request.user):
        messages.error(request, 'You are already enrolled in this course.')
        return redirect(course.get_absolute_url())
    
    # Create or get pending enrollment
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'status': 'pending',
            'is_paid': False
        }
    )
    
    # Check for existing pending payment
    from .models import CoursePayment
    existing_payment = CoursePayment.objects.filter(
        user=request.user,
        course=course,
        status__in=['pending', 'processing']
    ).first()
    
    if existing_payment:
        # Update existing payment with new reference
        import uuid
        while True:
            new_reference = f"REF_{uuid.uuid4().hex[:10].upper()}"
            if not CoursePayment.objects.filter(reference=new_reference).exists():
                break
        
        existing_payment.reference = new_reference
        existing_payment.status = 'pending'
        existing_payment.save()
        payment = existing_payment
    else:
        # Create new payment record
        import uuid
        while True:
            reference = f"REF_{uuid.uuid4().hex[:10].upper()}"
            if not CoursePayment.objects.filter(reference=reference).exists():
                break
        
        payment = CoursePayment.objects.create(
            user=request.user,
            course=course,
            enrollment=enrollment,
            amount=course.price,
            payment_method='kora_pay',
            status='pending',
            reference=reference
        )
    
    # Initialize payment with Kora Pay
    import requests
    
    kora_pay_data = {
        "amount": int(course.price),
        "currency": "NGN", 
        "reference": payment.reference,
        "redirect_url": request.build_absolute_uri('/payment/verify/'),
        "notification_url": request.build_absolute_uri('/payment/webhook/'),
        "narration": f"Payment for {course.title}",
        "channels": ["card", "bank_transfer", "pay_with_bank"],
        "customer": {
            "email": request.user.email,
            "name": request.user.get_full_name() or request.user.username
        },
        "metadata": {
            "course_id": str(course.id),
            "user_id": str(request.user.id),
            "payment_id": str(payment.id),
            "signup_checkout": "true"  # Flag to identify signup-checkout flow
        }
    }
    
    headers = {
        "Authorization": f"Bearer {settings.KORA_PAY_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{settings.KORA_PAY_BASE_URL}/charges/initialize",
            json=kora_pay_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('status'):
                # Store payment details and redirect to checkout
                payment.payment_details = response_data
                payment.save()
                
                # Don't show a message here - it will persist after payment
                return redirect(response_data['data']['checkout_url'])
            else:
                error_msg = response_data.get('message', 'Payment initialization failed')
                payment.mark_as_failed(error_msg)
                messages.error(request, f'Payment initialization failed: {error_msg}')
        else:
            error_msg = f'HTTP {response.status_code}: {response.text}'
            payment.mark_as_failed(error_msg)
            messages.error(request, 'Payment service unavailable. Please try again.')
            
    except requests.RequestException as e:
        error_msg = f'Network error: {str(e)}'
        payment.mark_as_failed(error_msg)
        messages.error(request, 'Network error. Please try again.')
    
    return redirect(course.get_absolute_url())


def initiate_course_payment(request, course_id):
    """Initiate payment for course enrollment"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if course is free
    if course.is_free:
        messages.error(request, 'This course is free. No payment required.')
        return redirect(course.get_absolute_url())
    
    # Check if already enrolled
    if course.is_enrolled_by_user(request.user):
        messages.error(request, 'You are already enrolled in this course.')
        return redirect(course.get_absolute_url())
    
    # Get or create enrollment
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'status': 'pending',
            'is_paid': False
        }
    )
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'kora_pay_public_key': settings.KORA_PAY_PUBLIC_KEY,
    }
    
    return render(request, 'payment/course_payment.html', context)


def process_course_payment(request):
    """Process course payment via Kora Pay"""
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'})
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            course_id = data.get('course_id')
            payment_method = data.get('payment_method', 'kora_pay')
        else:
            course_id = request.POST.get('course_id')
            payment_method = request.POST.get('payment_method', 'kora_pay')
        
        if not course_id:
            return JsonResponse({'success': False, 'error': 'Course ID is required'})
            
        try:
            course = Course.objects.get(id=course_id, status='published')
        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Course not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error finding course: {str(e)}'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Request processing error: {str(e)}'})
    
    # Check if user already has a completed enrollment for this course
    existing_enrollment = CourseEnrollment.objects.filter(
        user=request.user,
        course=course,
        status='completed',
        is_paid=True
    ).first()
    
    if existing_enrollment:
        return JsonResponse({
            'success': False,
            'error': 'You have already purchased this course. Please check your enrolled courses.'
        })
    
    # Check if there's already a pending/processing payment
    from .models import CoursePayment
    existing_payment = CoursePayment.objects.filter(
        user=request.user,
        course=course,
        status__in=['pending', 'processing']
    ).first()
    
    if existing_payment:
        # User already has a pending payment, generate new unique reference for retry
        import uuid
        while True:
            new_reference = f"REF_{uuid.uuid4().hex[:10].upper()}"
            # Check if this reference is already used by any payment
            if not CoursePayment.objects.filter(reference=new_reference).exists():
                break
        
        existing_payment.reference = new_reference
        existing_payment.status = 'pending'
        existing_payment.save()
        payment = existing_payment
        enrollment = existing_payment.enrollment
    else:
        # Get or create enrollment (this handles the case where admin removed enrollment)
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'status': 'pending',
                'is_paid': False
            }
        )
        
        # Try to get or create payment record to avoid constraint issues
        payment, created = CoursePayment.objects.get_or_create(
            user=request.user,
            course=course,
            enrollment=enrollment,
            defaults={
                'amount': course.price,
                'payment_method': 'kora_pay',  # Use string value, not model instance
                'status': 'pending'
            }
        )
        
        # If payment already exists, update it
        if not created:
            # Generate new unique reference for retry to avoid duplicate reference error
            import uuid
            while True:
                new_reference = f"REF_{uuid.uuid4().hex[:10].upper()}"
                # Check if this reference is already used by any payment
                if not CoursePayment.objects.filter(reference=new_reference).exists():
                    break
            
            payment.reference = new_reference
            payment.amount = course.price
            payment.payment_method = 'kora_pay'  # Use string value, not model instance
            payment.status = 'pending'
            payment.save()
        else:
            # Even for new payments, ensure unique reference
            import uuid
            while True:
                new_reference = f"REF_{uuid.uuid4().hex[:10].upper()}"
                if not CoursePayment.objects.filter(reference=new_reference).exists():
                    break
            
            payment.reference = new_reference
            payment.save()
    
    # Initialize payment with Kora Pay
    import requests
    
    kora_pay_data = {
        "amount": int(course.price),  # Amount in naira
        "currency": "NGN",
        "reference": payment.reference,
        "redirect_url": request.build_absolute_uri('/payment/verify/'),
        "notification_url": request.build_absolute_uri('/payment/webhook/'),
        "narration": f"Payment for {course.title}",
        "channels": ["card", "bank_transfer", "pay_with_bank"],
        "customer": {
            "email": request.user.email,
            "name": request.user.get_full_name() or request.user.username
        },
        "metadata": {
            "course_id": str(course.id),
            "user_id": str(request.user.id),
            "payment_id": str(payment.id),
        }
    }
    
    headers = {
        "Authorization": f"Bearer {settings.KORA_PAY_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{settings.KORA_PAY_BASE_URL}/charges/initialize",
            json=kora_pay_data,
            headers=headers
        )
        
        print(f"Kora Pay API URL: {settings.KORA_PAY_BASE_URL}/charges/initialize")
        print(f"Request headers: {headers}")
        print(f"Request data: {kora_pay_data}")
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('status'):
                # Store the checkout URL in payment details
                payment.payment_details = response_data
                payment.save()
                
                return JsonResponse({
                    'success': True,
                    'payment_url': response_data['data']['checkout_url'],
                    'checkout_url': response_data['data']['checkout_url'],
                    'reference': payment.reference
                })
            else:
                error_msg = response_data.get('message', 'Payment initialization failed')
                payment.mark_as_failed(error_msg)
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                })
        else:
            error_msg = f'HTTP {response.status_code}: {response.text}'
            payment.mark_as_failed(error_msg)
            return JsonResponse({
                'success': False,
                'error': f'Payment service error: {error_msg}'
            })
            
    except requests.RequestException as e:
        error_msg = f'Network error: {str(e)}'
        payment.mark_as_failed(error_msg)
        return JsonResponse({
            'success': False,
            'error': f'Network error: {str(e)}'
        })
    
    return JsonResponse({'success': False, 'error': 'Payment method not supported'})


def verify_payment(request):
    """Verify payment with Kora Pay and complete enrollment"""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference')
        return redirect('courses')
    
    try:
        from .models import CoursePayment
        payment = CoursePayment.objects.get(reference=reference)
    except CoursePayment.DoesNotExist:
        messages.error(request, 'Payment not found')
        return redirect('courses')
    
    # Verify with Kora Pay
    import requests
    
    headers = {
        "Authorization": f"Bearer {settings.KORA_PAY_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{settings.KORA_PAY_BASE_URL}/charges/{reference}",
            headers=headers
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('status') and response_data.get('data'):
                transaction_data = response_data['data']
                transaction_status = transaction_data.get('status')
                
                if transaction_status == 'success':
                    if payment.status == 'pending':
                        # Mark payment as completed
                        payment.external_transaction_id = transaction_data.get('payment_reference', reference)
                        payment.payment_details.update(transaction_data)
                        payment.mark_as_completed()
                        
                        # Check if this was a signup-checkout flow
                        metadata = payment.payment_details.get('metadata', {})
                        is_signup_checkout = metadata.get('signup_checkout') == 'true'
                        
                        if is_signup_checkout:
                            # Welcome new user and announce successful enrollment
                            messages.success(request, f'Welcome to Website Designer Nigeria, {payment.user.get_full_name() or payment.user.username}! Payment successful - you are now enrolled in {payment.course.title}!')
                        else:
                            # Regular purchase success message
                            messages.success(request, f'Payment successful! You are now enrolled in {payment.course.title}')
                    else:
                        # Payment already processed - ensure enrollment is completed
                        payment.mark_as_completed()  # This ensures enrollment status is also updated
                        messages.info(request, f'You are already enrolled in {payment.course.title}')
                    
                    return redirect(payment.course.get_absolute_url())
                    
                elif transaction_status == 'failed':
                    payment.mark_as_failed('Payment failed at gateway')
                    messages.error(request, 'Payment failed. Please try again.')
                    return redirect('initiate_course_payment', course_id=payment.course.id)
                    
                elif transaction_status == 'pending':
                    messages.info(request, 'Payment is still being processed. Please check back shortly.')
                    return redirect(payment.course.get_absolute_url())
                    
                elif transaction_status in ['cancelled', 'abandoned']:
                    payment.mark_as_failed('Payment cancelled by user')
                    messages.warning(request, 'Payment was cancelled. You can try again to complete your purchase.')
                    return redirect('initiate_course_payment', course_id=payment.course.id)
                    
                else:
                    # For any other unknown status
                    messages.info(request, f'Payment status: {transaction_status}. Please contact support if you need assistance.')
                    return redirect(payment.course.get_absolute_url())
            else:
                messages.error(request, 'Unable to verify payment status')
                return redirect('courses')
                
    except requests.RequestException as e:
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('courses')
    
    messages.info(request, 'Payment verification completed')
    return redirect(payment.course.get_absolute_url())


def payment_success(request):
    """Payment success page"""
    reference = request.GET.get('reference')
    
    if reference:
        try:
            from .models import CoursePayment
            payment = CoursePayment.objects.get(reference=reference, status='completed')
            context = {
                'payment': payment,
                'course': payment.course
            }
            return render(request, 'payment/success.html', context)
        except CoursePayment.DoesNotExist:
            pass
    
    return render(request, 'payment/success.html')


def payment_failed(request):
    """Payment failed page"""
    reference = request.GET.get('reference')
    
    if reference:
        try:
            from .models import CoursePayment
            payment = CoursePayment.objects.get(reference=reference)
            if payment.status != 'completed':
                payment.mark_as_failed('Payment cancelled by user')
            
            context = {
                'payment': payment,
                'course': payment.course
            }
            return render(request, 'payment/failed.html', context)
        except CoursePayment.DoesNotExist:
            pass
    
    return render(request, 'payment/failed.html')


@csrf_exempt
def kora_pay_webhook(request):
    """Handle Kora Pay webhook notifications"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    try:
        import json
        payload = json.loads(request.body.decode('utf-8'))
        
        # Verify webhook is from Kora Pay
        event = payload.get('event')
        if event != 'charge.success':
            return HttpResponse(status=200)  # Acknowledge other events
        
        data = payload.get('data', {})
        reference = data.get('reference')
        
        if not reference:
            return HttpResponse(status=400)
        
        # Find the payment
        try:
            from .models import CoursePayment
            payment = CoursePayment.objects.get(reference=reference)
        except CoursePayment.DoesNotExist:
            return HttpResponse(status=404)
        
        # Only process if payment is still pending
        if payment.status == 'pending':
            # Verify the payment amount matches
            expected_amount = int(payment.amount * 100)  # Convert to kobo
            received_amount = data.get('amount', 0)
            
            if expected_amount == received_amount:
                # Mark payment as completed
                payment.external_transaction_id = data.get('payment_reference', reference)
                payment.payment_details.update(data)
                payment.mark_as_completed()
                
                # Log successful webhook processing
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Webhook processed successfully for payment {payment.transaction_id}")
            else:
                # Amount mismatch - mark as failed
                payment.mark_as_failed(f"Amount mismatch: expected {expected_amount}, received {received_amount}")
        
        return HttpResponse(status=200)
        
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    except Exception as e:
        # Log the error but return 200 to acknowledge receipt
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Webhook processing error: {str(e)}")
        return HttpResponse(status=200)


def lecture_detail(request, course_slug, lecture_id):
    """
    Display individual lecture content with access control
    """
    course = get_object_or_404(Course, slug=course_slug)
    lecture = get_object_or_404(Lecture, id=lecture_id, section__course=course)
    
    # Check if user has access to this lecture
    user_enrolled = False
    has_access = False
    
    if request.user.is_authenticated:
        # Check if user is properly enrolled (paid)
        user_enrolled = course.is_enrolled_by_user(request.user)
        
        # For free courses, auto-enroll if not already enrolled
        if course.is_free and not user_enrolled:
            enrollment, created = CourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 'enrolled',
                    'is_paid': True
                }
            )
            user_enrolled = True
    
    # Access control - preview lectures or enrolled users or staff
    has_access = (
        lecture.is_preview or 
        user_enrolled or 
        (request.user.is_authenticated and request.user.is_staff)
    )
    
    if not has_access:
        if course.is_free:
            messages.error(request, 'You need to enroll in this course to access this lecture.')
        else:
            messages.error(request, 'You need to purchase this course to access this lecture.')
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
