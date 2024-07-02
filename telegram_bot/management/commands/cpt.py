from django.core.management.base import BaseCommand
from habits.tasks import send_habit_reminders

class Command(BaseCommand):
    help = 'Send habit reminders'

    def handle(self, *args, **kwargs):
        send_habit_reminders()