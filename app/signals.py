# # filepath: c:\Users\WDN\Desktop\websitedesigner\app\signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# from onesignal_sdk.client import Client
# from .models import Blog  # Replace with your actual blog post model

# @receiver(post_save, sender=Blog)
# def send_push_notification(sender, instance, created, **kwargs):
#     if created:  # Only send notification for new posts
#         client = Client(app_id=settings.ONESIGNAL_APP_ID, rest_api_key=settings.ONESIGNAL_API_KEY)
#         notification = {
#             "headings": {"en": "New Blog Post!"},
#             "contents": {"en": f"{instance.title} is now live!"},
#             "included_segments": ["All"]  # Send to all subscribers
#         }
#         response = client.send_notification(notification)
#         print(response)  # Optional: Log the response