import os
from celery import shared_task
import requests
from django.utils import timezone

from habits.models import Habit

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'


@shared_task
def send_habit_reminders(*args, **kwargs):
    now = timezone.now()
    habits = Habit.objects.filter(time__lte=now)
    for habit in habits:
        if habit.user.telegram_id:
            message = f"Reminder: It's time to do your habit - {habit.action}"
            params = {
                'chat_id': habit.user.telegram_id,
                'text': message,
            }
            response = requests.get(TELEGRAM_API_URL, params=params)
            response.raise_for_status()