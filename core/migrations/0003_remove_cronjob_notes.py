# Generated by Django 5.0.6 on 2025-01-19 01:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cronjob_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cronjob',
            name='notes',
        ),
    ]
