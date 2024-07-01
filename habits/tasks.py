import os

from celery import shared_task
import requests
from django.apps import apps
from telegram_bot.tasks import TELEGRAM_API_URL


@shared_task
def send_habit_reminders(habit_id):
    Habit = apps.get_model('habits', 'Habit')
    try:
        habit = Habit.objects.get(id=habit_id)
        if habit.user.telegram_id:
            message = f"Reminder: It's time to do your habit - {habit.action}"
            params = {
                'chat_id': habit.user.telegram_id,
                'text': message,
            }
            response = requests.get(TELEGRAM_API_URL, params=params)
            response.raise_for_status()
    except Habit.DoesNotExist:
        pass