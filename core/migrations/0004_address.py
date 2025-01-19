# Generated by Django 5.0.6 on 2025-01-19 12:18

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_cronjob_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='country')),
                ('city', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='city')),
                ('province', models.CharField(blank=True, max_length=100, null=True, verbose_name='province')),
                ('address_name', models.CharField(max_length=200, verbose_name='address name')),
                ('detail', models.CharField(blank=True, max_length=200, null=True, verbose_name='address detail')),
                ('date_creation', models.DateField(auto_now_add=True, verbose_name='date creation')),
                ('odoo_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='odoo id')),
                ('schedule_min_1', models.TimeField(blank=True, null=True, verbose_name='schedule min 1')),
                ('schedule_max_1', models.TimeField(blank=True, null=True, verbose_name='schedule max 1')),
                ('schedule_min_2', models.TimeField(blank=True, null=True, verbose_name='schedule min 2')),
                ('schedule_max_2', models.TimeField(blank=True, null=True, verbose_name='schedule max 2')),
            ],
            options={
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
                'ordering': ('address_name',),
                'indexes': [models.Index(fields=['address_name', 'city'], name='core_addres_address_6dc7dd_idx')],
            },
        ),
    ]
