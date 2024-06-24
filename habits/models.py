from django.contrib.auth.models import User
from django.db import models


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    frequency = models.PositiveIntegerField(default=1)
    reward = models.CharField(max_length=255, null=True, blank=True)
    duration = models.PositiveIntegerField()
    is_public = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.duration > 120:
            raise ValueError("Duration cannot exceed 120 seconds")
        if self.related_habit and self.reward:
            raise ValueError("Cannot have both a related habit and a reward")
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValueError("Pleasant habit cannot have reward or related habit")
        if self.frequency < 1 or self.frequency > 7:
            raise ValueError("Frequency must be between 1 and 7 days")
        super().save(*args, **kwargs)
