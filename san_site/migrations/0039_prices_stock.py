# Generated by Django 2.1.1 on 2018-09-16 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('san_site', '0038_auto_20180914_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='prices',
            name='stock',
            field=models.BooleanField(default=False),
        ),
    ]
