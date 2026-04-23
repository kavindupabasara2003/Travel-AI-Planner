import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_ai_backend.settings')

app = Celery('travel_ai_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
