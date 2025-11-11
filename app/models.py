from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_display_name(self):
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs')
    date = models.DateTimeField(default=timezone.now)
    meta_description = models.TextField(blank=True, null=True) 
    content = RichTextField()
    image = models.ImageField(upload_to='blog_images/')
    comments_count = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['-date']
        
    def normalized_category(self):
        return slugify(self.category)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={
            'category_slug': self.category.slug,
            'slug': self.slug
        })

class BlogSidebarBanner(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)  # Optional title for the banner
    image = models.ImageField(upload_to='banners/')  # Upload path for the images
    link = models.URLField(blank=True, null=True)  # Optional link for the banner
    order = models.PositiveIntegerField(default=0)  # For ordering banners

    class Meta:
        ordering = ['order']  # Ensure banners are displayed in the specified order

    def __str__(self):
        return self.title if self.title else f"Banner {self.id}"
    
class BlogslistSidebarBanner(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)  # Optional title for the banner
    image = models.ImageField(upload_to='blogs-banners/')  # Upload path for the images
    link = models.URLField(blank=True, null=True)  # Optional link for the banner
    order = models.PositiveIntegerField(default=0)  # For ordering banners

    class Meta:
        ordering = ['order']  # Ensure banners are displayed in the specified order

    def __str__(self):
        return self.title if self.title else f"Banner {self.id}"
    

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.blog.title}'


class WorkshopRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    social_media_link = models.URLField(help_text="Link to your X/TikTok post")
    linkedin_profile = models.URLField(help_text="Your LinkedIn profile URL")
    payment_receipt = models.FileField(upload_to='workshop_receipts/', help_text="Upload payment receipt image or PDF")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Admin notes")
    pin = models.CharField(max_length=20, blank=True, null=True, help_text="Unique PIN for participant")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Workshop Registration"
        verbose_name_plural = "Workshop Registrations"

    def __str__(self):
        return f'{self.full_name} - {self.email} ({self.status})'


class ConsultationBooking(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('new-website', 'New Website'),
        ('redesign', 'Website Redesign'),
        ('ecommerce', 'E-commerce Store'),
        ('maintenance', 'Website Maintenance'),
        ('other', 'Other'),
    ]
    
    CONSULTATION_TYPE_CHOICES = [
        ('video-call', 'Video Call'),
        ('phone-call', 'Phone Call'),
        ('in-person', 'In-Person Meeting'),
        ('whatsapp', 'WhatsApp Consultation'),
    ]
    
    BUDGET_CHOICES = [
        ('under-100k', 'Under ₦100,000'),
        ('100k-300k', '₦100,000 - ₦300,000'),
        ('300k-500k', '₦300,000 - ₦500,000'),
        ('500k-1m', '₦500,000 - ₦1,000,000'),
        ('over-1m', 'Over ₦1,000,000'),
        ('not-sure', 'Not sure yet'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    # Project Information
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    timeline = models.CharField(max_length=50, blank=True)
    project_description = models.TextField(blank=True)
    current_website = models.URLField(blank=True)
    inspiration = models.TextField(blank=True)
    
    # Consultation Preferences
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE_CHOICES)
    preferred_date = models.DateField(blank=True, null=True)
    preferred_time = models.CharField(max_length=20, blank=True)
    session_duration = models.CharField(max_length=10, blank=True, help_text="Duration in minutes (20, 40, or 60)")
    consultation_cost = models.CharField(max_length=20, blank=True, help_text="Cost in Naira")
    
    # Additional Services
    additional_services = models.TextField(blank=True)  # Store as comma-separated values
    
    # System Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)  # For admin notes
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation Booking'
        verbose_name_plural = 'Consultation Bookings'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.project_type} ({self.status})'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_additional_services_list(self):
        if self.additional_services:
            return [service.strip() for service in self.additional_services.split(',')]
        return []


# Course Platform Models
class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon")
    
    class Meta:
        verbose_name_plural = "Course Categories"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Instructor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='instructors/', blank=True, null=True)
    expertise = models.CharField(max_length=500, help_text="Comma-separated expertise areas")
    years_experience = models.PositiveIntegerField(default=0)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True, help_text="WhatsApp contact link for enrolled students")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    students_count = models.PositiveIntegerField(default=0)
    courses_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    def get_total_students_count(self):
        """Get total enrolled students across all instructor's courses"""
        total = 0
        for course in self.courses.filter(status='published'):
            total += course.get_enrolled_students_count()
        return total
    
    @property
    def dynamic_students_count(self):
        """Return the sum of manual student counts from all published courses"""
        total = 0
        for course in self.courses.filter(status='published'):
            total += course.students_count
        return total


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('coming_soon', 'Coming Soon'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    subtitle = models.CharField(max_length=500, blank=True)
    description = RichTextField()
    short_description = models.TextField(max_length=500)
    
    # Course Details
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    language = models.CharField(max_length=50, default='English')
    
    # Media
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    preview_video = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    
    # Course Stats
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    reviews_count = models.PositiveIntegerField(default=0)
    students_count = models.PositiveIntegerField(default=0)
    
    # Course Content
    total_duration = models.PositiveIntegerField(default=0, help_text="Total duration in minutes")
    lectures_count = models.PositiveIntegerField(default=0)
    
    # What students will learn
    learning_objectives = models.TextField(help_text="One objective per line")
    prerequisites = models.TextField(blank=True, help_text="One prerequisite per line")
    target_audience = models.TextField(blank=True, help_text="One target per line")
    
    # Meta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO
    meta_description = models.TextField(blank=True, max_length=160)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})
    
    def get_discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    def get_learning_objectives_list(self):
        return [obj.strip() for obj in self.learning_objectives.split('\n') if obj.strip()]
    
    def get_prerequisites_list(self):
        if self.prerequisites:
            return [req.strip() for req in self.prerequisites.split('\n') if req.strip()]
        return []
    
    def get_target_audience_list(self):
        if self.target_audience:
            return [target.strip() for target in self.target_audience.split('\n') if target.strip()]
        return []
    
    def is_enrolled_by_user(self, user):
        """Check if a user is enrolled in this course with paid status"""
        if not user.is_authenticated:
            return False
        return self.enrollments.filter(user=user, status='enrolled', is_paid=True).exists()
    
    def has_pending_payment(self, user):
        """Check if user has pending payment for this course"""
        if not user.is_authenticated:
            return False
        return self.enrollments.filter(user=user, status='pending').exists()
    
    def get_user_enrollment(self, user):
        """Get user's enrollment for this course"""
        if not user.is_authenticated:
            return None
        try:
            return self.enrollments.get(user=user)
        except CourseEnrollment.DoesNotExist:
            return None
    
    def can_user_access(self, user):
        """Check if user can access course content"""
        if not user.is_authenticated:
            return False
        if self.is_free:
            return True
        return self.is_enrolled_by_user(user)
    
    def can_user_review(self, user):
        """Check if a user can review this course (must be enrolled and not already reviewed)"""
        if not user.is_authenticated:
            return False
        is_enrolled = self.is_enrolled_by_user(user)
        has_reviewed = self.reviews.filter(user=user).exists()
        return is_enrolled and not has_reviewed
    
    def get_user_review(self, user):
        """Get user's review for this course if exists"""
        if not user.is_authenticated:
            return None
        try:
            return self.reviews.get(user=user)
        except CourseReview.DoesNotExist:
            return None
    
    def update_rating_from_reviews(self):
        """Update course rating based on approved reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            from django.db.models import Avg
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 2) if avg_rating else 0.00
            self.reviews_count = reviews.count()
        else:
            self.rating = 0.00
            self.reviews_count = 0
        self.save(update_fields=['rating', 'reviews_count'])
    
    def get_enrolled_students_count(self):
        """Get actual number of enrolled students"""
        return self.enrollments.filter(status='enrolled').count()
    
    @property
    def dynamic_students_count(self):
        """Return the manual student count set in admin"""
        return self.students_count
    
    def get_total_lectures_count(self):
        """Calculate total number of lectures across all sections"""
        total = 0
        for section in self.sections.all():
            total += section.lectures.count()
        return total
    
    def get_total_duration_calculated(self):
        """Calculate total duration from all lectures"""
        total = 0
        for section in self.sections.all():
            total += section.get_total_duration()
        return total
    
    def update_course_stats(self):
        """Update lectures_count and total_duration fields"""
        self.lectures_count = self.get_total_lectures_count()
        self.total_duration = self.get_total_duration_calculated()
        self.save(update_fields=['lectures_count', 'total_duration'])
    
    @property
    def total_lectures(self):
        """Property to get total lectures count (uses stored value or calculates)"""
        if self.lectures_count > 0:
            return self.lectures_count
        return self.get_total_lectures_count()
    
    @property
    def total_course_duration(self):
        """Property to get total duration (uses stored value or calculates)"""
        if self.total_duration > 0:
            return self.total_duration
        return self.get_total_duration_calculated()
    
    def update_rating_from_reviews(self):
        """Calculate and update course rating based on approved reviews"""
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            total_rating = sum(review.rating for review in approved_reviews)
            avg_rating = total_rating / approved_reviews.count()
            self.rating = round(avg_rating, 2)
            self.reviews_count = approved_reviews.count()
        else:
            self.rating = 0.00
            self.reviews_count = 0
        self.save(update_fields=['rating', 'reviews_count'])


class CourseSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Uncheck to make all lectures in this section inaccessible (show padlock)")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_total_duration(self):
        """Calculate total duration of all lectures in this section"""
        return sum(lecture.duration for lecture in self.lectures.all())


class Lecture(models.Model):
    LECTURE_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]
    
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = RichTextField(blank=True)
    lecture_type = models.CharField(max_length=20, choices=LECTURE_TYPES, default='video')
    
    # Video content
    video_url = models.URLField(blank=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes")
    
    # File attachments
    attachments = models.FileField(upload_to='lecture_attachments/', blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Can be viewed without enrollment")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.section.course.title} - {self.title}"


class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    helpful_users = models.ManyToManyField(User, related_name='helpful_reviews', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['course', 'user']
    
    def __str__(self):
        return f"{self.course.title} - {self.rating} stars by {self.user.username}"
    
    @property
    def student_name(self):
        """Backward compatibility property"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def student_email(self):
        """Backward compatibility property"""
        return self.user.email
    
    def mark_helpful(self):
        """Increment helpful count"""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])
    
    def toggle_helpful(self, user):
        """Toggle helpful status for a user"""
        if user in self.helpful_users.all():
            # Remove helpful
            self.helpful_users.remove(user)
            self.helpful_count = max(0, self.helpful_count - 1)
            is_helpful = False
        else:
            # Add helpful
            self.helpful_users.add(user)
            self.helpful_count += 1
            is_helpful = True
        
        self.save(update_fields=['helpful_count'])
        return is_helpful
    
    def is_helpful_by_user(self, user):
        """Check if user has marked this review as helpful"""
        if not user.is_authenticated:
            return False
        return self.helpful_users.filter(id=user.id).exists()


class CourseEnrollment(models.Model):
    """Track course enrollments/purchases"""
    ENROLLMENT_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)  # Track if payment was made for paid courses
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Course completion percentage
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class CoursePayment(models.Model):
    """Track course payment transactions"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('kora_pay', 'Kora Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card Payment'),
        ('pay_with_bank', 'Pay with Bank'),
        ('mobile_money', 'Mobile Money'),
    ]
    
    # Basic Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    enrollment = models.OneToOneField(CourseEnrollment, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Transaction IDs
    transaction_id = models.CharField(max_length=100, unique=True)  # Our internal transaction ID
    external_transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Payment provider's transaction ID
    reference = models.CharField(max_length=100, unique=True)  # Payment reference
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Details
    payment_details = models.JSONField(default=dict, blank=True)  # Store additional payment provider data
    failure_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user.username} - {self.course.title}"
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        import uuid
        return f"TXN_{uuid.uuid4().hex[:12].upper()}"
    
    def generate_reference(self):
        """Generate unique payment reference"""
        import uuid
        return f"REF_{uuid.uuid4().hex[:10].upper()}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)
    
    def mark_as_completed(self, external_transaction_id=None):
        """Mark payment as completed and enroll user"""
        self.status = 'completed'
        self.paid_at = timezone.now()
        if external_transaction_id:
            self.external_transaction_id = external_transaction_id
        self.save()
        
        # Update enrollment status
        if self.enrollment:
            self.enrollment.status = 'enrolled'
            self.enrollment.is_paid = True
            self.enrollment.save()
    
    def mark_as_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        self.save()


class ConsultationPayment(models.Model):
    """Track consultation payment transactions"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('kora_pay', 'Kora Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card Payment'),
        ('pay_with_bank', 'Pay with Bank'),
        ('mobile_money', 'Mobile Money'),
    ]
    
    # Basic Info
    consultation_booking = models.OneToOneField(ConsultationBooking, on_delete=models.CASCADE, related_name='payment')
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Transaction IDs
    transaction_id = models.CharField(max_length=100, unique=True)  # Our internal transaction ID
    external_transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Payment provider's transaction ID
    reference = models.CharField(max_length=100, unique=True)  # Payment reference
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Details
    payment_details = models.JSONField(default=dict, blank=True)  # Store additional payment provider data
    failure_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation Payment'
        verbose_name_plural = 'Consultation Payments'
    
    def __str__(self):
        return f"Payment for {self.consultation_booking.full_name} - ₦{self.amount} ({self.status})"
    
    def mark_as_completed(self):
        """Mark payment as completed and update consultation booking status"""
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.consultation_booking.status = 'confirmed'
        self.consultation_booking.save()
        self.save()
    
    def mark_as_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        self.save()


# Signals to automatically update course statistics
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Lecture)
def update_course_stats_on_lecture_change(sender, instance, **kwargs):
    """Update course statistics when lectures are added, modified, or deleted"""
    try:
        course = instance.section.course
        course.update_course_stats()
    except:
        pass  # Handle any potential errors gracefully

@receiver([post_save, post_delete], sender=CourseSection)
def update_course_stats_on_section_change(sender, instance, **kwargs):
    """Update course statistics when sections are added or deleted"""
    try:
        course = instance.course
        course.update_course_stats()
    except:
        pass  # Handle any potential errors gracefully

@receiver([post_save, post_delete], sender=CourseReview)
def update_course_rating_on_review_change(sender, instance, **kwargs):
    """Update course rating when reviews are added, modified, or deleted"""
    try:
        course = instance.course
        course.update_rating_from_reviews()
    except:
        pass  # Handle any potential errors gracefully