from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Command(BaseCommand):
    help = 'Create periodic tasks for sending habit reminders'

    def handle(self, *args, **kwargs):
        # Create or get the interval schedule
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        # Create or update the periodic task
        PeriodicTask.objects.update_or_create(
            name='Send Habit Reminders',
            defaults={
                'interval': schedule,
                'task': 'telegram_bot.tasks.send_habit_reminders',
                'args': json.dumps([1]),  # Assuming habit_id 1 for demonstration
            }
        )
        self.stdout.write(self.style.SUCCESS('Periodic task created/updated successfully'))
