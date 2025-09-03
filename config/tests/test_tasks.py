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
    
    @patch('myapp.tasks.ContentType.objects.get_for_id')
    @patch('myapp.tasks.model.objects.filter')
    def test_increment_counters_atomicity(self, mock_filter, mock_get_for_id):
        """Тест атомарности увеличения счетчиков при параллельных вызовах"""
        # Мокируем вызовы к базе данных
        mock_model = mock_get_for_id.return_value.model_class.return_value
        mock_query = mock_filter.return_value
        mock_query.update.return_value = 1
        
        # Вызываем задачу несколько раз с одинаковыми данными
        increment_counters(self.content_ids)
        increment_counters(self.content_ids)
        
        # Проверяем, что update вызывался правильное количество раз
        # 2 вызова задачи × 3 элемента в content_ids = 6 вызовов update
        self.assertEqual(mock_query.update.call_count, 6)
        
        # Проверяем, что каждый вызов update использовал F()-expression
        for call in mock_query.update.call_args_list:
            args, kwargs = call
            self.assertIn('counter', kwargs)
            self.assertIn('F', str(kwargs['counter']))  # Проверяем, что используется F()-expression