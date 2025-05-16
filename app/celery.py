from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Redis as broker
app.conf.broker_url = 'redis://127.0.0.1:6379/0'

# Redis for results
app.conf.result_backend = 'redis://127.0.0.1:6379/0'

# Beat schedule to run the task every hour
app.conf.beat_schedule = {
    'calculate-performance-every-hour': {
        'task': 'your_app_name.tasks.calculate_all_restaurants_performance',
        'schedule': 10,  # Every hour at the start of the hour
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
