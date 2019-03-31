from __future__ import absolute_import, unicode_literals

import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')

app = Celery('san_site')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1800.0, orders_request.s('orders_request'), name='orders_request')
    sender.add_periodic_task(crontab(hour=5, minute=30),
                             change_relevant_products.s('change_relevant_products'), name='change_relevant_products')
    sender.add_periodic_task(crontab(hour=4, minute=30),
                             create_files_customers.s('create_files_customers'), name='create_files_customers')
    sender.add_periodic_task(crontab(hour=3, minute=30),
                             reindex_db.s('reindex_db'), name='reindex_db')


@app.task
def orders_request(arg):
    from san_site.models import Order
    Order.orders_request()


@app.task
def create_files_customers(arg):
    from san_site.backend.create_files import create_files_customers
    create_files_customers()


@app.task
def change_relevant_products(arg):
    from san_site.models import Product
    Product.change_relevant_products()


@app.task
def reindex_db(arg):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""DO $$
          BEGIN
            PERFORM ReindexDb();
          END;
          $$;""")
