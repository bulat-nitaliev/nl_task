from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Page
from .serializers import PageListSerializer, PageDetailSerializer
from .tasks import increment_content_counters

class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.prefetch_related('pagecontent_set__content_object').all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PageListSerializer
        return PageDetailSerializer
    
    def list(self, request, *args, **kwargs):
        # Пагинация списка страниц
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        # Получение детальной информации о странице
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Отправка задачи на увеличение счетчиков в фоне
        content_ids = []
        for page_content in instance.pagecontent_set.all():
            content_ids.append((page_content.content_type_id, page_content.object_id))
        
        # Асинхронное увеличение счетчиков
        print(content_ids)
        increment_content_counters.delay(content_ids)
        
        return Response(serializer.data)