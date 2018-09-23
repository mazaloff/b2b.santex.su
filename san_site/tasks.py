from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from Project.celery import app
from .models import Order, Product, Person


@app.task(bind=True)
def order_request(self, order_id):
    order = Order.objects.get(id=order_id)
    try:
        order.request_order()
    except Order.RequestOrderError as exc:
        self.retry(exc=exc, max_retries=10, countdown=90)


@app.task(bind=True)
def change_relevant_products(self):
    Product.change_relevant_products()


@app.task(bind=True)
def letter_password_change(self, user_id, url):
    user = User.objects.get(id=user_id)
    try:
        person = user.person
    except Person.DoesNotExist:
        return
    try:
        person.letter_password_change(url)
    except Person.LetterPasswordChangeError as exc:
        self.retry(exc=exc, max_retries=10, countdown=60)
