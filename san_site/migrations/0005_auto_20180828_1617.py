# Generated by Django 2.1 on 2018-08-28 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('san_site', '0004_auto_20180827_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventories',
            name='product_guid',
        ),
        migrations.RemoveField(
            model_name='inventories',
            name='stores_guid',
        ),
        migrations.AddField(
            model_name='inventories',
            name='product',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='san_site.Product'),
        ),
        migrations.AddField(
            model_name='inventories',
            name='store',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='san_site.Store'),
        ),
    ]