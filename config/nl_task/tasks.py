
from celery import shared_task
from django.db.models import F
from django.contrib.contenttypes.models import ContentType


@shared_task
def increment_counters(content_ids):
    for content_type_id, object_id in content_ids:
        content_type = ContentType.objects.get_for_id(content_type_id)
        model = content_type.model_class()
        model.objects.filter(id=object_id).update(counter=F('counter') + 1)