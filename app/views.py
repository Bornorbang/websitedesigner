from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

# Create your views here.

def home(request):
    return render(request, 'index.html')

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
