# Generated by Django 5.0.6 on 2024-06-24 13:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=255)),
                ('time', models.TimeField()),
                ('action', models.CharField(max_length=255)),
                ('is_pleasant', models.BooleanField(default=False)),
                ('frequency', models.PositiveIntegerField(default=1)),
                ('reward', models.CharField(blank=True, max_length=255, null=True)),
                ('duration', models.PositiveIntegerField()),
                ('is_public', models.BooleanField(default=False)),
                ('related_habit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='habits.habit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
