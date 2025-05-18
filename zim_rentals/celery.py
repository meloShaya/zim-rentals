import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zim_rentals.settings')

app = Celery('zim_rentals')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-new-listings-daily': {
        'task': 'listings.tasks.check_new_listings_for_saved_searches',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
        'args': (),
    },
    'cleanup-old-saved-searches': {
        'task': 'listings.tasks.cleanup_old_saved_searches',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Run weekly on Sunday at 2 AM
        'args': (),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 