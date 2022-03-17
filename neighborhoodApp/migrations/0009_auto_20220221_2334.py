# Generated by Django 3.2.9 on 2022-02-21 23:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoodApp', '0008_auto_20220211_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='accuracy',
        ),
        migrations.AddField(
            model_name='users',
            name='geohash',
            field=models.CharField(default=0, max_length=30),
        ),
        migrations.AddField(
            model_name='users',
            name='geohash_length',
            field=models.IntegerField(default=9),
        ),
        migrations.AddField(
            model_name='users',
            name='neighberhood_layers',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)]),
        ),
    ]
