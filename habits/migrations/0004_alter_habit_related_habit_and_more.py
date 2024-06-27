# Generated by Django 5.0.6 on 2024-06-27 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0003_rename_time_of_pleasant_habit_habit_pleasant_habit_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='related_habit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='habits.habit'),
        ),
        migrations.RemoveField(
            model_name='habit',
            name='pleasant_habit_time',
        ),
        migrations.AddField(
            model_name='habit',
            name='is_pleasant',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='PleasantHabit',
        ),
    ]