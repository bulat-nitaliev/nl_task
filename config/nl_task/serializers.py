# serializers.py
from rest_framework import serializers
from .models import Page, Video, Audio, Content
from django.contrib.contenttypes.models import ContentType

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['order', 'content_object']

    def to_representation(self, instance):
        content = instance.content_object
        if isinstance(content, Video):
            serializer = VideoSerializer(content)
        elif isinstance(content, Audio):
            serializer = AudioSerializer(content)
        else:
            raise Exception("Unknown content type")
        
        # Добавляем порядок к данным контента
        data = serializer.data
        data['order'] = instance.order
        return data

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'counter', 'video_url', 'subtitle_url']

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ['id', 'title', 'counter', 'text']

class PageSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='page-detail')
    
    class Meta:
        model = Page
        fields = ['id', 'title', 'url']

class PageDetailSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(source='contents.all', many=True)

    class Meta:
        model = Page
        fields = ['id', 'title', 'contents']