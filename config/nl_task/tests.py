from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from .models import Page, Video, Audio, Text, PageContent
from .factories import PageFactory, VideoFactory, AudioFactory, TextFactory, PageContentFactory
from faker import Faker



class PageAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Создаем несколько страниц с контентом
        self.pages = PageFactory.create_batch(5)
        fake = Faker()
        for page in self.pages:
            # Добавляем разный контент к каждой странице
            for i in range(3):
                content_factory = fake.random_element([VideoFactory, AudioFactory, TextFactory])
                content = content_factory()
                PageContentFactory.create(page=page, content_object=content, order=i)
    
    def test_list_pages(self):
        """Тест получения списка страниц с пагинацией"""
        url = reverse('page-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        
        # Проверяем, что данные корректны
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(len(response.data['results']), 5)
        
        # Проверяем наличие URL для детальной информации
        for page_data in response.data['results']:
            self.assertIn('url', page_data)
            self.assertIn('title', page_data)
    
    
    
    def test_retrieve_page_detail(self):
        """Тест получения детальной информации о странице"""
        page = self.pages[0]
        url = reverse('page-detail', kwargs={'pk': page.pk})
        
        # Мокаем Celery task
        with patch('nl_task.tasks.increment_content_counters.delay') as mock_task:
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['id'], page.id)
            self.assertEqual(response.data['title'], page.title)
            
            # Проверяем, что контент присутствует
            self.assertIn('contents', response.data)
            self.assertGreater(len(response.data['contents']), 0)
            
            # Проверяем структуру контента
            for content in response.data['contents']:
                self.assertIn('content', content)
                self.assertIn('order', content)
                self.assertIn('title', content['content'])
                self.assertIn('counter', content['content'])
            
            # Проверяем, что задача Celery была вызвана
            self.assertTrue(mock_task.called)
    
    def test_content_counters_increment(self):
        """Тест увеличения счетчиков просмотров"""
        page = self.pages[0]
        url = reverse('page-detail', kwargs={'pk': page.pk})
        
        # Мокаем Celery task, но имитируем ее выполнение
        with patch('nl_task.tasks.increment_content_counters.delay') as mock_task:
            # Вызываем детальное представление
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Проверяем, что задача была вызвана с правильными аргументами
            self.assertTrue(mock_task.called)
            
            # Получаем аргументы, с которыми была вызвана задача
            call_args = mock_task.call_args[0][0]
            
            # Проверяем, что в вызове правильное количество элементов
            self.assertEqual(len(call_args), page.pagecontent_set.count())
    
   
    
    def test_page_not_found(self):
        """Тест обработки несуществующей страницы"""
        url = reverse('page-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ContentModelTest(TestCase):
    def test_video_creation(self):
        """Тест создания видео контента"""
        video = VideoFactory()
        self.assertIsNotNone(video.id)
        self.assertIsNotNone(video.title)
        self.assertIsNotNone(video.video_file_url)
    
    def test_audio_creation(self):
        """Тест создания аудио контента"""
        audio = AudioFactory()
        self.assertIsNotNone(audio.id)
        self.assertIsNotNone(audio.title)
        self.assertIsNotNone(audio.text)
    
    def test_text_creation(self):
        """Тест создания текстового контента"""
        text = TextFactory()
        self.assertIsNotNone(text.id)
        self.assertIsNotNone(text.title)
        self.assertIsNotNone(text.content)
    
