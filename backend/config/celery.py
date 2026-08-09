"""
Celery configuration for LandMarket project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('landmarket')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'apps.authentication.tasks.cleanup_expired_sessions',
        'schedule': 3600.0,  # Run every hour
    },
    'update-property-verification-scores': {
        'task': 'apps.properties.tasks.update_verification_scores',
        'schedule': 86400.0,  # Run daily
    },
    'send-pending-notifications': {
        'task': 'apps.messaging.tasks.send_pending_notifications',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

app.conf.timezone = 'Asia/Kolkata'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')