import datetime
import json

from django.conf import settings
from django.db import models
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import connection

json.JSONEncoder.default = lambda self, obj: \
    (obj.isoformat() if isinstance(obj, (datetime.datetime, datetime.date)) else None)


# connection.queries


class SectionManager(models.Manager):
    pass


class Customer(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Person(models.Model):
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    change_password = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Section(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    parent_guid = models.CharField(max_length=50, db_index=True)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SectionManager()

    def __str__(self):
        return self.name

    def list_with_children(self, list_sections):
        list_sections.append(self)
        children = Section.objects.filter(parent_guid=self.guid, is_deleted=False)
        for child in children:
            list_sections.append(child)
            child.list_with_children(list_sections)

    def add_current_session(self, request):
        request.session['id_current_session'] = self.id
        request.session.modified = True

    @staticmethod
    def get_current_session(request):
        return request.session.get('id_current_session')

    @staticmethod
    def get_goods_list(user, list_sections=None, search=None, only_stock=None, only_promo=None):

        list_res_ = []
        currency_dict = {elem_.id: elem_.name for elem_ in Currency.objects.all()}

        set_products = Product.objects.filter(is_deleted=False)

        if list_sections is not None:
            set_products = set_products.filter(section__in=list_sections)

        if only_promo == 'true':
            set_products = set_products.filter(id__in=PricesSale.objects.all().values("product_id"))

        if search is not None and search != '':
            set_products = set_products.filter(Q(code__icontains=search) | Q(name__icontains=search))

        if user.is_authenticated:

            current_customer = get_customer(user)
            if current_customer is None:
                return list_res_

            products = set_products.order_by('code').prefetch_related(
                Prefetch('product_inventories', queryset=Inventories.objects.all()),
                Prefetch('product_prices', queryset=Prices.objects.all()),
                Prefetch('product_customers_prices',
                         queryset=CustomersPrices.objects.filter(customer=current_customer)))

            for value_product in products:
                quantity_sum = 0
                for product_inventories in value_product.product_inventories.all():
                    quantity_sum += product_inventories.quantity
                price_value, price_discount, price_percent = (0, 0, 0)
                currency_name, promo = ('', False)
                for product_prices in value_product.product_prices.all():
                    price_value = product_prices.value
                    price_discount = product_prices.value
                    promo = product_prices.promo
                    currency_name = currency_dict.get(product_prices.currency_id, '')
                for product_prices in value_product.product_customers_prices.all():
                    price_discount = product_prices.discount
                    price_percent = product_prices.percent
                for product_prices in value_product.product_prices.all():
                    price_value = product_prices.value
                    promo = product_prices.promo
                    if currency_name == '':
                        currency_name = currency_dict.get(product_prices.currency_id, '')
                if only_stock == 'true' and quantity_sum <= 0:
                    continue
                list_res_.append({
                    'product': value_product,
                    'guid': value_product.guid,
                    'code': value_product.code,
                    'name': value_product.name,
                    'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                    'price': '' if price_value == 0 else price_value,
                    'promo': promo,
                    'discount': '' if price_discount == 0 else price_discount,
                    'currency': currency_name,
                    'percent': '' if price_percent == 0 else price_percent,
                }
                )

        else:

            products = set_products.order_by('code').prefetch_related(
                Prefetch('product_inventories', queryset=Inventories.objects.all()),
                Prefetch('product_prices', queryset=Prices.objects.all()),
                Prefetch('product_prices_sale', queryset=PricesSale.objects.all()))

            for value_product in products:
                quantity_sum = 0
                for product_inventories in value_product.product_inventories.all():
                    quantity_sum += product_inventories.quantity
                price_value = 0
                currency_name, promo = ('', False)
                for product_prices in value_product.product_prices_sale.all():
                    price_value = product_prices.value
                    currency_name = currency_dict.get(product_prices.currency_id, '')
                    promo = True
                if price_value == 0:
                    for product_prices in value_product.product_prices.all():
                        price_value = product_prices.value
                        currency_name = currency_dict.get(product_prices.currency_id, '')
                if only_stock == 'true' and quantity_sum <= 0:
                    continue
                list_res_.append({
                    'product': value_product,
                    'guid': value_product.guid,
                    'code': value_product.code,
                    'name': value_product.name,
                    'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                    'price': '' if price_value == 0 else price_value,
                    'promo': promo,
                    'discount': '',
                    'currency': currency_name,
                    'percent': '',
                }
                )

        return list_res_

    def get_goods_list_section(self, user, search=None, only_stock=None, only_promo=None):
        list_sections = []
        self.list_with_children(list_sections)
        return Section.get_goods_list(
            user=user, list_sections=list_sections, search=search, only_stock=only_stock, only_promo=only_promo)


class Product(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=30, db_index=True)
    sort = models.IntegerField(default=500)
    section = models.ForeignKey(Section, db_index=True, on_delete=models.PROTECT)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name

    def get_price(self, user):

        current_customer = get_customer(user)
        if current_customer is None:
            return dict(price=0, price_ruble=0, currency_name='', currency_id=0)

        query_set_price = CustomersPrices.objects. \
            filter(customer=current_customer, product=self).select_related('currency')
        if len(query_set_price):
            currency = query_set_price[0].currency
            currency_name = query_set_price[0].currency.name
            currency_id = query_set_price[0].currency.id
            price = query_set_price[0].discount
            price_ruble = currency.change_ruble(price)
            return dict(price=price, price_ruble=price_ruble, currency_name=currency_name, currency_id=currency_id)
        return dict(price=0, price_ruble=0, currency_name='', currency_id=0)


class Store(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Price(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Currency(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def get_ruble():
        try:
            currency = Currency.objects.get(code='643')
        except Currency.DoesNotExist:
            return
        return currency.id

    def get_today_course(self):
        from django.db.models import Max
        dict_max_date = Courses.objects.filter(currency=self).aggregate(max_date=Max('date'))
        if not dict_max_date['max_date'] is None:
            set_course = Courses.objects.filter(currency=self).filter(date=dict_max_date['max_date'])
            if len(set_course) > 0:
                return {'course': set_course[0].course, 'multiplicity': set_course[0].multiplicity}
        return {'course': 1, 'multiplicity': 1}

    def change_ruble(self, value):
        course = self.get_today_course()
        return round(value * course['course'] / course['multiplicity'], 2)


class Inventories(models.Model):
    product = models.ForeignKey(Product, related_name='product_inventories',
                                db_index=True, on_delete=models.PROTECT)
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)


class Prices(models.Model):
    product = models.ForeignKey(Product, related_name='product_prices',
                                db_index=True, on_delete=models.PROTECT)
    promo = models.BooleanField(default=False)
    price = models.ForeignKey(Price, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    value = models.FloatField(default=0)


class PricesSale(models.Model):
    product = models.ForeignKey(Product, related_name='product_prices_sale',
                                db_index=True, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    value = models.FloatField(default=0)


class CustomersPrices(models.Model):
    customer = models.ForeignKey(Customer, db_index=True, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='product_customers_prices',
                                db_index=True, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    discount = models.FloatField(default=0)
    percent = models.FloatField(default=0)


class Courses(models.Model):
    date = models.DateField(db_index=True)
    currency = models.ForeignKey(Currency, db_index=True, on_delete=models.PROTECT)
    course = models.FloatField(default=0)
    multiplicity = models.IntegerField(default=1)


class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    person = models.ForeignKey(Person, db_index=True, on_delete=models.PROTECT)
    guid = models.CharField(max_length=50, db_index=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    delivery = models.DateTimeField(null=True)
    shipment = models.CharField(max_length=50, choices=settings.SHIPMENT_TYPE, null=True)
    payment = models.CharField(max_length=50, choices=settings.PAYMENT_FORM, null=True)
    status = models.CharField(max_length=50, choices=settings.STATUS_ORDER, default='Новый')
    comment = models.TextField(null=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def __iter__(self):
        for item in self.items.all():
            dict_ = dict(
                product=item.product,
                code=item.product.code,
                guid=item.product.guid,
                name=item.product.name,
                price=item.price,
                currency=item.currency,
                price_ruble=item.price_ruble,
                quantity=item.quantity
            )
            dict_['total_price'] = round(item.price * item.quantity, 2)
            dict_['total_price_ruble'] = round(item.price_ruble * item.quantity, 2)

            yield dict_

    def get_order_list(self):
        list_res_ = []
        for element in self:
            list_res_.append(element)
        return list_res_

    @staticmethod
    def get_orders_list(user):
        set_person = Person.objects.filter(user=user)
        if len(set_person) == 0:
            return []
        orders = Order.objects.filter(person=set_person[0])
        return orders

    def get_json_for_request(self):
        rest = dict(guid=self.guid,
                    date=self.date,
                    number=self.id,
                    customer=self.person.customer.guid,
                    delivery=self.delivery,
                    shipment=self.shipment,
                    payment=self.payment,
                    comment=self.comment
                    )
        rest_items = []
        for item in self:
            rest_item = dict(
                product=item['guid'],
                quantity=item['quantity'])
            rest_items.append(rest_item)
        rest['items'] = rest_items
        return json.dumps(rest)

    def request_order(self):
        import requests

        api_url = settings.API_URL + r'Order/OrderCreate/'

        data = self.get_json_for_request()

        params = {
            'Content-Type': 'application/json'}

        answer = requests.post(api_url, data=data, headers=params)
        if answer.status_code != 200:
            pass
        try:
            dict_obj = answer.json()
        except json.decoder.JSONDecodeError:
            return
        if dict_obj.get('success', None) is None:
            return
        result = dict_obj.get('result', None)
        if result is None:
            return
        if len(result) == 0:
            return
        if result[0]['number'] != self.id:
            return
        self.guid = result[0]['guid']
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=Currency.get_ruble)
    price_ruble = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return round(self.price_ruble * self.quantity, 2)


def get_customer(user):
    person = user.person
    if person:
        return person.customer
