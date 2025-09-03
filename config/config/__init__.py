from .celery import app as celery_app
from datetime import datetime

__all__ = ('celery_app',)

print(__name__, "name", datetime.now())