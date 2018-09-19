from __future__ import absolute_import, unicode_literals
from Project.celery import app
from .models import Order, Product


@app.task(bind=True)
def order_request(self, order_id):
    order = Order.objects.get(id=order_id)
    try:
        order.request_order()
    except Order.RequestOrderError as exc:
        self.retry(exc=exc, max_retries=10, countdown=60)


@app.task(bind=True)
def change_relevant_products(self):
    Product.change_relevant_products()
