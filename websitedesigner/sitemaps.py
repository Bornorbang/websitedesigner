from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app.models import Blog, Category  # Import your Blog and Category models

class StaticSitemap(Sitemap):
    def items(self):
        return ['home', 'about-website-designer-nigeria', 'services', 'contact', 'website_lagos', 'seo_services', 'blogs']

    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse('blog_detail', kwargs={'category_slug': obj.category.slug, 'slug': obj.slug})

class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_posts', kwargs={'category_slug': obj.slug})