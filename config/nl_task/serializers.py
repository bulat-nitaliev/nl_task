from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Page, Video, Audio, Text, PageContent

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = '__all__'

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'

class ContentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # Динамическая сериализация в зависимости от типа контента
        content_type = ContentType.objects.get_for_model(instance.__class__)
        if content_type.model == 'video':
            return VideoSerializer(instance).data
        elif content_type.model == 'audio':
            return AudioSerializer(instance).data
        elif content_type.model == 'text':
            return TextSerializer(instance).data
        return {}

class PageContentSerializer(serializers.ModelSerializer):
    # Используем content_object вместо content
    content = serializers.SerializerMethodField()
    
    class Meta:
        model = PageContent
        fields = ('content', 'order')
    
    def get_content(self, obj):
        # Сериализуем связанный объект контента
        return ContentSerializer(obj.content_object).data

class PageListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = ('id', 'title', 'created_at', 'url')
    
    def get_url(self, obj):
        # Правильное построение абсолютного URL
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(reverse('page-detail', kwargs={'pk': obj.pk}))
        return reverse('page-detail', kwargs={'pk': obj.pk})

class PageDetailSerializer(serializers.ModelSerializer):
    # Используем правильное имя related_name
    contents = PageContentSerializer(
        source='pagecontent_set', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = Page
        fields = ('id', 'title', 'created_at', 'contents')