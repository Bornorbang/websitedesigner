from django.contrib.sitemaps import Sitemap
from django.urls import reverse  # Import reverse to get static URLs

class StaticSitemap(Sitemap):
    def items(self):
        # Return a list of static URLs (view names) you want to include in the sitemap
        return ['home', 'about-website-designer-nigeria', 'services', 'contact']  # Replace these with your actual view names

    def location(self, item):
        # Dynamically generate the URL for each view name
        return reverse(item)
