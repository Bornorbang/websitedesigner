from django.contrib import admin
from .models import *

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'date', 'comments_count')
    prepopulated_fields = {'slug': ('title',)}

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
