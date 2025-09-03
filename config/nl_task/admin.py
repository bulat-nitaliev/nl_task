# admin.py
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Page, Video, Audio, Content

class ContentInline(GenericTabularInline):
    model = Content
    extra = 1
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    classes = ('collapse',)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    inlines = [ContentInline]

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'counter')
    search_fields = ('title',)

@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'counter')
    search_fields = ('title',)