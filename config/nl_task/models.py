# models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Page(models.Model):
    title = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['title']

class Content(models.Model):
    page = models.ForeignKey(Page, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class ContentBase(models.Model):
    title = models.CharField(max_length=255)
    counter = models.PositiveIntegerField(default=0)
    pages = GenericRelation(Content, related_query_name='content_base')

    class Meta:
        abstract = True

class Video(ContentBase):
    video_url = models.URLField()
    subtitle_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['title']

class Audio(ContentBase):
    text = models.TextField()
    
    class Meta:
        ordering = ['title']