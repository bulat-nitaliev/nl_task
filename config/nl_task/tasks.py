from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from config import celery_app

@celery_app.task
def increment_content_counters(content_ids):
    """
    Атомарное увеличение счетчиков просмотров для контента
    """
    for content_type_id, object_id in content_ids:
        # Получаем модель по content_type_id
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)
            model_class = content_type.model_class()
            
            # Атомарное обновление счетчика
            with transaction.atomic():
                model_class.objects.filter(id=object_id).update(counter=F('counter') + 1)
                
        except (ContentType.DoesNotExist, Exception) as e:
            # Логируем ошибку, но не прерываем выполнение для других элементов
            print(f"Error updating counter for {content_type_id}-{object_id}: {e}")
            continue