from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
import requests

from .models import Blog, Category, BlogSidebarBanner, BlogslistSidebarBanner, Comment


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
