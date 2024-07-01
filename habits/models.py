from django.contrib.auth.models import User
from django.db import models
from .validators import (
    validate_reward_and_related_habit,
    validate_duration,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit_no_reward_or_related,
    validate_frequency
)


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='bound_habits')
    frequency = models.PositiveIntegerField(default=1)
    reward = models.CharField(max_length=255, null=True, blank=True)
    duration = models.PositiveIntegerField()
    is_public = models.BooleanField(default=False)

    def clean(self):
        validate_reward_and_related_habit(self.reward, self.related_habit)
        validate_duration(self.duration)
        validate_pleasant_habit_no_reward_or_related(self)
        validate_frequency(self.frequency)
        if self.related_habit:
            validate_related_habit_is_pleasant(self.related_habit)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

