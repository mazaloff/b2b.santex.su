# Generated by Django 2.1.1 on 2018-09-16 13:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('san_site', '0040_auto_20180916_1605'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prices',
            old_name='stock',
            new_name='promo',
        ),
    ]
