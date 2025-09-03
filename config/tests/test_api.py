import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from unittest.mock import patch
from tests.factories import PageFactory, VideoContentFactory, AudioContentFactory

# Для тестирования с синхронным выполнением Celery задач
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class PageAPITests(APITestCase):
    
    def setUp(self):
        # Создаем несколько страниц с контентом
        self.page1 = PageFactory()
        self.page2 = PageFactory()
        
        # Добавляем контент к страницам
        self.video_content1 = VideoContentFactory(page=self.page1)
        self.audio_content1 = AudioContentFactory(page=self.page1)
        self.video_content2 = VideoContentFactory(page=self.page2)
        
        self.list_url = reverse('page-list')
        self.detail_url = reverse('page-detail', kwargs={'pk': self.page1.pk})
    
    def test_get_page_list(self):
        """Тест получения списка страниц с пагинацией"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn('url', response.data['results'][0])
    
    def test_get_page_list_pagination(self):
        """Тест пагинации списка страниц"""
        # Создаем дополнительные страницы для тестирования пагинации
        for _ in range(15):
            PageFactory()
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # PAGE_SIZE по умолчанию
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    
    def test_get_page_list_search(self):
        """Тест поиска по заголовку страниц"""
        # Создаем страницу с уникальным заголовком
        unique_title = "UniqueTestPage123"
        special_page = PageFactory(title=unique_title)
        
        response = self.client.get(f"{self.list_url}?search=UniqueTestPage")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], unique_title)
    
    def test_get_page_detail(self):
        """Тест получения детальной информации о странице"""
        initial_video_counter = self.video_content1.content_object.counter
        initial_audio_counter = self.audio_content1.content_object.counter
        
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.page1.id)
        self.assertEqual(response.data['title'], self.page1.title)
        
        # Проверяем, что контент присутствует в ответе
        self.assertEqual(len(response.data['contents']), 2)
        
        # Проверяем, что счетчики увеличились (благодаря CELERY_TASK_ALWAYS_EAGER)
        self.video_content1.content_object.refresh_from_db()
        self.audio_content1.content_object.refresh_from_db()
        
        self.assertEqual(self.video_content1.content_object.counter, initial_video_counter + 1)
        self.assertEqual(self.audio_content1.content_object.counter, initial_audio_counter + 1)
    
    def test_page_detail_content_order(self):
        """Тест порядка контента на странице"""
        # Создаем контент с разным порядком
        video_low_order = VideoContentFactory(page=self.page1, order=1)
        video_high_order = VideoContentFactory(page=self.page1, order=5)
        
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем порядок контента
        orders = [item['order'] for item in response.data['contents']]
        self.assertEqual(orders, sorted(orders))
    
    def test_page_detail_content_structure(self):
        """Тест структуры контента в ответе"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что видео контент имеет правильные поля
        video_content = next(item for item in response.data['contents'] 
                            if 'video_url' in item)
        self.assertIn('video_url', video_content)
        self.assertIn('subtitle_url', video_content)
        self.assertIn('counter', video_content)
        self.assertIn('title', video_content)
        
        # Проверяем, что аудио контент имеет правильные поля
        audio_content = next(item for item in response.data['contents'] 
                            if 'text' in item)
        self.assertIn('text', audio_content)
        self.assertIn('counter', audio_content)
        self.assertIn('title', audio_content)
    
    @patch('myapp.tasks.increment_counters.delay')
    def test_counters_incremented_in_background(self, mock_delay):
        """Тест, что увеличение счетчиков происходит в фоновой задаче"""
        # Отключаем синхронное выполнение задач для этого теста
        with override_settings(CELERY_TASK_ALWAYS_EAGER=False):
            initial_video_counter = self.video_content1.content_object.counter
            initial_audio_counter = self.audio_content1.content_object.counter
            
            response = self.client.get(self.detail_url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Проверяем, что задача была отправлена
            self.assertTrue(mock_delay.called)
            
            # Проверяем, что счетчики НЕ увеличились сразу
            self.video_content1.content_object.refresh_from_db()
            self.audio_content1.content_object.refresh_from_db()
            
            self.assertEqual(self.video_content1.content_object.counter, initial_video_counter)
            self.assertEqual(self.audio_content1.content_object.counter, initial_audio_counter)