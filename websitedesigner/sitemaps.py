from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app.models import Blog, Category  # Import your Blog and Category models

class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return [
            'home', 
            'about-website-designer-nigeria', 
            'services', 
            'contact', 
            'website_lagos', 
            'seo_services', 
            'blogs', 
            'tech_tips', 
            'tech_reviews', 
            'courses', 
            'advertise', 
            'consultation', 
            'pricing',
            'shopify_pricing',
            'seo_pricing',
            'sm_pricing',
            'portfolio',
            'earn_money',
            'terms',
            'privacy',
            '20_days_with_wdn',
            'ecommerce',
            'graphic_design',
            'consultation_booking'
        ]

    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    
    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse('blog_detail', kwargs={'category_slug': obj.category.slug, 'slug': obj.slug})

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    
    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_posts', kwargs={'category_slug': obj.slug})