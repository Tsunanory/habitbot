# Generated by Django 5.0.6 on 2024-07-01 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='last_reminder_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
