# Generated by Django 5.0.6 on 2025-01-19 12:18

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ubigeo', models.CharField(db_index=True, max_length=80, validators=[django.core.validators.MinLengthValidator(6)])),
                ('name', models.CharField(db_index=True, max_length=80)),
                ('capital', models.CharField(db_index=True, max_length=80)),
                ('department', models.CharField(db_index=True, max_length=80)),
                ('province', models.CharField(db_index=True, max_length=80)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('odoo_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='odoo id')),
            ],
            options={
                'verbose_name': 'District',
                'verbose_name_plural': 'Districts',
                'ordering': ['department', 'province', 'name'],
                'indexes': [models.Index(fields=['department', 'province', 'name'], name='shipping_di_departm_fcf812_idx'), models.Index(fields=['ubigeo'], name='shipping_di_ubigeo_597007_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='district',
            constraint=models.UniqueConstraint(fields=('department', 'province', 'name'), name='unique_district_location'),
        ),
    ]
