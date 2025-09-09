from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
import requests

from .models import Blog, Category, BlogSidebarBanner, BlogslistSidebarBanner, Comment, ConsultationBooking, Course, CourseCategory, Instructor, CourseSection, Lecture, CourseReview, CourseEnrollment


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'date', 'comments_count', 'send_notification_button')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('send_notification_button',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:post_id>/send-notification/', self.admin_site.admin_view(self.send_notification), name='send_notification'),
        ]
        return custom_urls + urls

    def send_notification_button(self, obj):
        if not obj.pk:
            return "-"
        url = reverse('admin:send_notification', args=[obj.pk])
        return format_html('<a class="button" href="{}">Send Notification</a>', url)
    send_notification_button.short_description = 'Push Notification'

    def send_notification(self, request, post_id, *args, **kwargs):
        blog = Blog.objects.get(pk=post_id)
        url = f"https://www.websitedesigner.ng{blog.get_absolute_url()}"
        payload = {
            "app_id": settings.ONESIGNAL_APP_ID,
            "included_segments": ["Subscribed Users"],
            "headings": {"en": blog.title},
            "contents": {"en": blog.meta_description or "Check out our latest blog post!"},
            "url": url
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
        }
        response = requests.post("https://onesignal.com/api/v1/notifications", json=payload, headers=headers)

        if response.status_code == 200:
            messages.success(request, f"Notification sent for '{blog.title}'")
        else:
            messages.error(request, f"Failed to send notification: {response.text}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogSidebarBanner)
class BlogSidebarBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)


@admin.register(BlogslistSidebarBanner)
class BlogslistSidebarBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'blog', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'content')


@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'project_type', 'consultation_type', 'status', 'created_at')
    list_filter = ('status', 'project_type', 'consultation_type', 'budget', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'company')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company', 'industry')
        }),
        ('Project Details', {
            'fields': ('project_type', 'budget', 'timeline', 'project_description', 'current_website', 'inspiration')
        }),
        ('Consultation Preferences', {
            'fields': ('consultation_type', 'preferred_date', 'preferred_time')
        }),
        ('Additional Information', {
            'fields': ('additional_services', 'status', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    full_name.short_description = 'Name'
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} consultations marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected consultations as confirmed'
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f'{queryset.count()} consultations marked as completed.')
    mark_as_completed.short_description = 'Mark selected consultations as completed'
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} consultations marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected consultations as cancelled'


# Course Platform Admin
@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'years_experience', 'rating', 'students_count', 'courses_count')
    search_fields = ('name', 'email', 'expertise')
    list_filter = ('years_experience', 'rating')
    readonly_fields = ('students_count', 'courses_count')


class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1
    fields = ('title', 'video_url', 'duration', 'is_preview', 'order', 'attachments')
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        # Show attachment status
        readonly = list(self.readonly_fields)
        return readonly


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 1
    fields = ('title', 'description', 'order', 'is_active')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'level', 'price', 'rating', 'students_count', 'status', 'created_at')
    list_filter = ('status', 'level', 'category', 'is_free', 'created_at')
    search_fields = ('title', 'description', 'instructor__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('rating', 'reviews_count', 'students_count', 'created_at', 'updated_at')
    list_editable = ('status', 'price')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'short_description', 'description')
        }),
        ('Course Details', {
            'fields': ('category', 'instructor', 'level', 'language', 'thumbnail', 'preview_video')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price', 'original_price')
        }),
        ('Content', {
            'fields': ('learning_objectives', 'prerequisites', 'target_audience', 'total_duration', 'lectures_count')
        }),
        ('Meta & SEO', {
            'fields': ('meta_description', 'status')
        }),
        ('Statistics', {
            'fields': ('rating', 'reviews_count', 'students_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CourseSectionInline]


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('title', 'course__title')
    list_editable = ('order', 'is_active')
    
    inlines = [LectureInline]


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'duration', 'is_preview', 'has_attachments', 'has_content', 'order')
    list_filter = ('is_preview', 'section__course')
    search_fields = ('title', 'section__title', 'section__course__title')
    list_editable = ('order', 'is_preview')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'section', 'order', 'is_preview')
        }),
        ('Video Content', {
            'fields': ('video_url', 'duration')
        }),
        ('Additional Resources', {
            'fields': ('content', 'attachments'),
            'description': 'Add rich text content for assignments/notes and file attachments for downloads'
        }),
    )
    
    def has_attachments(self, obj):
        return bool(obj.attachments)
    has_attachments.boolean = True
    has_attachments.short_description = 'Has Files'
    
    def has_content(self, obj):
        return bool(obj.content)
    has_content.boolean = True
    has_content.short_description = 'Has Content'


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'helpful_count', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('course__title', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'helpful_count')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'is_paid', 'progress', 'enrolled_at')
    list_filter = ('status', 'is_paid', 'enrolled_at')
    search_fields = ('user__username', 'user__email', 'course__title')
    list_editable = ('status', 'is_paid', 'progress')
    readonly_fields = ('enrolled_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')
