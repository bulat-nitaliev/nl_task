# views.py
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from .models import Page
from .serializers import PageSerializer, PageDetailSerializer
from .tasks import increment_counters

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PageListAPIView(generics.ListAPIView):
    serializer_class = PageSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        queryset = Page.objects.all()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            # Поиск по заголовку страницы и контента
            queryset = queryset.filter(
                Q(title__istartswith=search_query) |
                Q(contents__content_object__title__istartswith=search_query)
            ).distinct()
            
        return queryset

class PageDetailAPIView(generics.RetrieveAPIView):
    queryset = Page.objects.all()
    serializer_class = PageDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Отправка задачи на увеличение счетчиков
        content_ids = [
            (content.content_type_id, content.object_id)
            for content in instance.contents.all()
        ]
        increment_counters.delay(content_ids)
        
        return Response(serializer.data)