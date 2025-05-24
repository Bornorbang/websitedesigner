from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Blog
import requests
from django.conf import settings

@receiver(post_save, sender=Blog)
def send_onesignal_notification(sender, instance, created, **kwargs):
    if created:
        url = f"https://websitedesigner.ng{instance.get_absolute_url()}"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
        }

        payload = {
            "app_id": settings.ONESIGNAL_APP_ID,
            "included_segments": ["Subscribed Users"],
            "headings": {"en": "New Blog Post"},
            "contents": {"en": instance.title},
            "url": url
        }

        requests.post("https://onesignal.com/api/v1/notifications", json=payload, headers=headers)
