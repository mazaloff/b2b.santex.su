# Generated by Django 2.1.1 on 2018-09-03 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('san_site', '0016_auto_20180902_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomersPrices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(default=0)),
                ('discount', models.FloatField(default=0)),
                ('percent', models.FloatField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='currency',
            name='guid',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='price',
            name='guid',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='store',
            name='guid',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AddField(
            model_name='customersprices',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='san_site.Currency'),
        ),
        migrations.AddField(
            model_name='customersprices',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='san_site.Customer'),
        ),
        migrations.AddField(
            model_name='customersprices',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_customers_prices', to='san_site.Product'),
        ),
    ]