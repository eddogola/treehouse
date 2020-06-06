from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treehouse.settings')

app = Celery('treehouse')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()