def recent_posts(request):
    from app.models import Blog  # Import here to avoid early loading
    recent_posts = Blog.objects.all().order_by('-date')[:5]
    return {'recent_posts': recent_posts}
