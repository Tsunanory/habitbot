from django.core.exceptions import ValidationError

def validate_reward_and_related_habit(reward, related_habit):
    if reward and related_habit:
        raise ValidationError('Cannot have both a reward and a related habit.')


def validate_duration(duration):
    if duration > 120:
        raise ValidationError('Duration cannot exceed 120 seconds.')


def validate_related_habit_is_pleasant(related_habit):
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError('Only pleasant habits can be set as related habits.')


def validate_pleasant_habit_no_reward_or_related(habit):
    if habit.is_pleasant and (habit.reward or habit.related_habit):
        raise ValidationError('A pleasant habit cannot have a reward or a related habit.')


def validate_frequency(frequency):
    if frequency < 1 or frequency > 7:
        raise ValidationError('Frequency must be between 1 and 7 days.')
