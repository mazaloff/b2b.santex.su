# Generated by Django 2.1.1 on 2018-09-07 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('san_site', '0025_auto_20180907_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.IntegerField(choices=[(1, 'Наличные'), (2, 'Безналичные')], null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipment',
            field=models.IntegerField(choices=[(1, 'Самовывоз'), (2, 'Доставка')], null=True),
        ),
    ]