from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')

app = Celery('san_site')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1800.0, orders_request.s('orders_request'), name='orders_request')
    sender.add_periodic_task(crontab(hour=4, minute=30),
                             create_files_customers.s('create_files_customers'), name='create_files_customers')


@app.task
def orders_request(arg):
    from san_site.models import Order
    Order.orders_request()


@app.task
def create_files_customers(arg):
    from san_site.backend.create_files import create_files_customers
    create_files_customers()
