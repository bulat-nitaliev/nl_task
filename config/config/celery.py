import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings')

app = Celery('config')
app = Celery('config', broker=settings.CELERY_BROKER_URL)


app.config_from_object(f'django.conf:settings', namespace='CELERY')
# app.conf.broker_url = 'redis://redis:6379/0'
app.autodiscover_tasks()