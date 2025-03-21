from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils import timezone


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
    date = models.DateTimeField(default=timezone.now)  # Change this line
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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.blog.title}'