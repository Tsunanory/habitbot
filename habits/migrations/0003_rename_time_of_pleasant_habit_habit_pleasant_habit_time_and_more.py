# Generated by Django 5.0.6 on 2024-06-26 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0002_remove_habit_is_pleasant_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='habit',
            old_name='time_of_pleasant_habit',
            new_name='pleasant_habit_time',
        ),
        migrations.RemoveField(
            model_name='pleasanthabit',
            name='time',
        ),
    ]
