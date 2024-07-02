from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks(['habits', 'telegram_bot'])


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'send-habit-reminders-every-minute': {
        'task': 'telegram_bot.tasks.send_habit_reminders',
        'schedule': crontab(minute='*/1'),
    },
}
