# Generated by Django 5.0.6 on 2025-01-18 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cronjob',
            name='notes',
            field=models.CharField(help_text='Notes of the cron job', max_length=100, null=True, verbose_name='notes'),
        ),
    ]
