import gevent
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_n_project.settings')
app = Celery('my_n_project', broker='redis://localhost:6379')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
        'send-task-every-day-at-12-30': {
            'task': 'main.tasks.send_statistic',
            'schedule': crontab(hour=13, minute=40, day_of_week='*'),
        },
    }
