from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
from nl_task.tasks import increment_counters
from tests.factories import VideoFactory, AudioFactory

class TaskTests(TestCase):
    
    def setUp(self):
        self.video = VideoFactory(counter=10)
        self.audio = AudioFactory(counter=20)
        
        self.video_content_type = ContentType.objects.get_for_model(self.video)
        self.audio_content_type = ContentType.objects.get_for_model(self.audio)
        
        self.content_ids = [
            (self.video_content_type.id, self.video.id),
            (self.audio_content_type.id, self.audio.id),
            (self.video_content_type.id, self.video.id),  # Дубликат для проверки атомарности
        ]
    
    def test_increment_counters(self):
        """Тест атомарного увеличения счетчиков"""
        initial_video_counter = self.video.counter
        initial_audio_counter = self.audio.counter
        
        # Вызываем задачу
        increment_counters(self.content_ids)
        
        # Обновляем объекты из базы
        self.video.refresh_from_db()
        self.audio.refresh_from_db()
        
        # Проверяем, что счетчики увеличились правильно
        self.assertEqual(self.video.counter, initial_video_counter + 2)  # +2 из-за дубликата
        self.assertEqual(self.audio.counter, initial_audio_counter + 1)
    
   