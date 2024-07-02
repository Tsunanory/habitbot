import os
import logging
from celery import shared_task
import requests
from django.utils import timezone
from habits.models import Habit
from django.db import models

# Get the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def send_habit_reminders(*args, **kwargs):
    now = timezone.now()
    today = now.date()
    current_time = now.time()
    logger.info("Running send_habit_reminders task at %s", now)
    logger.info("Current time: %s", current_time)

    # Fetch habits that have not received a reminder today and whose time has passed
    habits = Habit.objects.filter(
        time__lte=current_time
    ).filter(
        models.Q(last_reminder_date__lt=today) | models.Q(last_reminder_date__isnull=True)
    )
    logger.info(f"Found {habits.count()} habits to remind")

    for habit in habits:
        logger.info(f"Processing habit ID: {habit.id}, Time: {habit.time}, Last Reminder Date: {habit.last_reminder_date}, User: {habit.user.username}")
        if habit.user.telegram_id:
            message = f"Reminder: It's time to do your habit - {habit.action} at {habit.place}"
            params = {
                'chat_id': habit.user.telegram_id,
                'text': message,
            }
            try:
                response = requests.get(TELEGRAM_API_URL, params=params)
                response.raise_for_status()  # Raise an error for bad status codes
                habit.last_reminder_date = today  # Update last reminder date
                habit.save()
                logger.info(f"Reminder sent to {habit.user.telegram_id} for habit {habit.action} in {habit.place}")
            except requests.RequestException as e:
                logger.error(f"Failed to send reminder to {habit.user.telegram_id} for habit {habit.action}: {e}")
        else:
            logger.warning(f"User {habit.user.username} does not have a telegram_id set")

def manual_send_habit_reminders():
    send_habit_reminders.apply()

if __name__ == "__main__":
    manual_send_habit_reminders()

