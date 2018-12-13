import datetime
import json
import requests
import pytz
import uuid

from django.db import connection
from django.conf import settings
from django.db import models
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import loader
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache

# connection.queries

# JSON section

json.JSONEncoder.default = lambda self, obj: \
    (obj.isoformat() if isinstance(obj, (datetime.datetime, datetime.date)) else None)


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d")
        except (ValueError, IndexError):
            pass
    return json_dict


# MODELS section


class SectionManager(models.Manager):
    pass


class Customer(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    guid_owner = models.CharField(max_length=50, db_index=True, default='---')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def get_customers_all_user(user):
        customer = get_customer(user)
        list_customers = []
        customers_all = Customer.objects.filter(guid_owner=customer.guid_owner)
        for elem in customers_all:
            list_customers.append((elem.guid, elem.name))
        return list_customers

    def get_files(self):
        customers_files = CustomersFiles.objects.filter(customer=self)
        files = []
        for elem in customers_files:
            files.append(dict(
                name=elem.name,
                view=elem.view,
                type=elem.type_file,
                url=elem.url + elem.name,
                change_date=elem.change_date
            ))
        return files


class Person(models.Model):
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    allow_order = models.BooleanField(default=False)
    key = models.CharField(max_length=20, default='xxx')
    uid = models.CharField(max_length=50, default='xxx')
    change_password = models.BooleanField(default=True)
    lock_order = models.BooleanField(default=False)

    class LetterPasswordChangeError(BaseException):
        pass

    def __str__(self):
        return self.name

    def letter_password_change(self, url):
        new_key = self.make_new_key()
        html_content = loader.render_to_string(
            'account/letter_change_password.html', {
                'person': self,
                'url': url + new_key + '/'
            }
        )
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(
            "Information for change your password!",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email])
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except Exception:
            if settings.CELERY_NO_SEND_EMAIL:
                return
            raise self.LetterPasswordChangeError

    def make_new_key(self, syllables=4, add_number=True):
        import random, string
        """Alternate random consonants & vowels creating decent memorable passwords
        """
        rnd = random.SystemRandom()
        s = string.ascii_lowercase
        vowels = 'aeiou'
        consonants = ''.join([x for x in s if x not in vowels])
        pwd = ''.join([rnd.choice(consonants) + rnd.choice(vowels)
                       for x in 'x' * syllables]).title()
        if add_number:
            pwd += str(rnd.choice(range(10)))
        self.key = pwd
        self.save()
        return pwd

    @property
    def lock(self):
        return self.lock_order

    @lock.setter
    def lock(self, value):
        if self.lock_order == value:
            return
        self.lock_order = value
        self.save()

    def create_uid(self):
        self.uid = str(uuid.uuid4()).replace('-', '')
        self.save()


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
        children = Section.objects.filter(parent_guid=self.guid)
        for child in children:
            child.list_with_children(list_sections)

    def add_current_session(self, request):
        request.session['id_current_session'] = self.id
        request.session.set_expiry(86400)
        request.session.modified = True

    @property
    def parent(self):
        if self.parent_guid != '---':
            try:
                return Section.objects.get(guid=self.parent_guid)
            except Section.DoesNotExist:
                return None

    @property
    def full_name(self):
        parents_name = self.create_parents_name()
        return parents_name + ('' if parents_name == '' else '/') + self.name

    def create_parents_name(self, full_name=''):
        parent = self.parent
        if parent or None:
            full_name = parent.name + ('' if full_name == '' else '/') + full_name
            full_name = parent.create_parents_name(full_name)
        return full_name

    @staticmethod
    def get_current_session(request):
        return request.session.get('id_current_session')

    @staticmethod
    def get_sessions():
        sections = cache.get('sessions')
        if sections is None:
            sections = Section.objects.filter(is_deleted=False).order_by('sort', 'name')
            cache.set('sessions', sections, 3600)
        return sections

    @staticmethod
    def get_data_for_tree():
        data = cache.get('data_for_tree')
        if data is None:
            sections = Section.get_sessions()
            data = []
            for obj in sections:
                parent = '#' if obj.parent_guid == '---' else obj.parent_guid
                data.append({'id': obj.guid, 'parent': parent, 'text': obj.name, 'href': obj.guid})
            cache.set('data_for_tree', data, 3600)
        return data

    @staticmethod
    def get_goods_list(**kwargs):

        user = kwargs.get('user', None)
        list_sections = kwargs.get('list_sections', None)
        search = kwargs.get('search', None)
        only_stock = kwargs.get('only_stock', 'false')
        only_promo = kwargs.get('only_promo', 'false')
        only_available = kwargs.get('only_available', 'true')

        only_stock = True if only_stock == 'true' or only_stock == True else False
        only_promo = True if only_promo == 'true' or only_promo == True else False
        only_available = True if only_available == 'true' or only_available == True else False

        list_res_ = []

        currency_dict = cache.get('currency_dict')
        if currency_dict is None:
            currency_dict: dict = {elem_.id: elem_.name for elem_ in Currency.objects.all()}
            cache.set('currency_dict', currency_dict, 8640)

        store_dict = cache.get('store_dict')
        if store_dict is None:
            store_dict: dict = {elem_.id: elem_.short_name for elem_ in Store.objects.all()}
            cache.set('store_dict', store_dict, 8640)

        set_products = Product.objects

        if only_available:
            set_products = set_products.filter(is_deleted=False)

        if list_sections is not None:
            set_products = set_products.filter(section__in=list_sections)

        if only_promo:
            set_products = set_products.filter(id__in=PricesSale.objects.all().values("product_id"))

        if search is not None and search != '':
            set_products = set_products.filter(Q(code__icontains=search) | Q(name__icontains=search))

        if user is not None and user.is_authenticated:

            current_customer = get_customer(user)
            if current_customer is None:
                return list_res_

            products = set_products.order_by('code').prefetch_related(
                Prefetch('product_inventories', queryset=Inventories.objects.all()),
                Prefetch('product_prices', queryset=Prices.objects.all()),
                Prefetch('product_customers_prices',
                         queryset=CustomersPrices.objects.filter(customer=current_customer)))

            for value_product in products:
                inventories = {}
                quantity_sum = 0
                for product_inventories in value_product.product_inventories.all():
                    quantity_sum += product_inventories.quantity
                    short_name = store_dict.get(product_inventories.store_id)
                    quantity = '>10' if product_inventories.quantity > 10 else product_inventories.quantity
                    inventories.update(dict([(short_name, quantity)]))
                price_value, price_discount, price_percent = (0, 0, 0)
                currency_name, currency_id, promo = ('', 0, False)
                for product_prices in value_product.product_prices.all():
                    price_value = product_prices.value
                    price_discount = price_value
                    promo = product_prices.promo
                    currency_id = product_prices.currency_id
                    currency_name = currency_dict.get(currency_id, '')
                for product_prices in value_product.product_customers_prices.all():
                    price_discount = product_prices.discount
                    price_percent = product_prices.percent
                # for product_prices in value_product.product_prices.all():
                #     price_value = product_prices.value
                #     promo = product_prices.promo
                #     if currency_name == '':
                #         currency_name = currency_dict.get(product_prices.currency_id, '')
                #         currency_id = product_prices.currency_id
                if only_stock and quantity_sum <= 0:
                    continue
                list_res_.append({
                    'product': value_product,
                    'guid': value_product.guid,
                    'code': value_product.code,
                    'name': value_product.name,
                    'relevant': value_product.is_relevant(),
                    'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                    'inventories': inventories,
                    'price': '' if price_value == 0 else price_value,
                    'promo': promo,
                    'discount': '' if price_discount == 0 else price_discount,
                    'currency': currency_name,
                    'currency_id': currency_id,
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
                currency_name, currency_id, promo = ('', 0, False)
                for product_prices in value_product.product_prices_sale.all():
                    price_value = product_prices.value
                    currency_id = product_prices.currency_id
                    currency_name = currency_dict.get(currency_id, '')
                    promo = True
                if price_value == 0:
                    for product_prices in value_product.product_prices.all():
                        price_value = product_prices.value
                        currency_id = product_prices.currency_id
                        currency_name = currency_dict.get(currency_id, '')
                if only_stock and quantity_sum <= 0:
                    continue
                list_res_.append({
                    'product': value_product,
                    'guid': value_product.guid,
                    'code': value_product.code,
                    'relevant': value_product.is_relevant(),
                    'name': value_product.name,
                    'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                    'price': '' if price_value == 0 else price_value,
                    'promo': promo,
                    'discount': '',
                    'currency': currency_name,
                    'currency_id': currency_id,
                    'percent': '',
                }
                )

        return list_res_

    def get_goods_list_section(self, **kwargs):

        list_sections = cache.get(f'list_sections_{self.id}')
        if list_sections is None:
            list_sections = []
            self.list_with_children(list_sections)
            cache.set(f'list_sections_{self.id}', list_sections, 8640)

        kwargs['list_sections'] = list_sections
        return Section.get_goods_list(**kwargs)


class Product(models.Model):
    RELEVANT_MATRIX = ('Акция', 'Заказной', 'Основной')

    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=30, db_index=True)
    sort = models.IntegerField(default=500)
    section = models.ForeignKey(Section, db_index=True, on_delete=models.PROTECT)
    matrix = models.CharField(max_length=30, default='Основной')
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name

    def is_relevant(self):
        return self.matrix in Product.RELEVANT_MATRIX

    @classmethod
    def change_relevant_products(cls):

        sections = Section.objects.filter(parent_guid='---')
        for obj_section in sections:
            goods_list = obj_section.get_goods_list_section(only_available=False)
            for element_list in goods_list:
                cur_object = element_list['product']
                if not cur_object.is_deleted:
                    if element_list['quantity'] == '' and element_list['price'] == '':
                        cur_object.is_deleted = True
                        cur_object.save()
                    elif element_list['quantity'] == '' and not element_list['relevant']:
                        cur_object.is_deleted = True
                        cur_object.save()
                elif element_list['relevant']:
                    if element_list['quantity'] != '' or element_list['price'] != '':
                        cur_object.is_deleted = False
                        cur_object.save()
                else:
                    if element_list['quantity'] != '':
                        cur_object.is_deleted = True
                        cur_object.save()

        sections = Section.objects.all()
        for obj_section in sections:
            is_active = len(obj_section.get_goods_list_section(only_available=True)) > 0
            if is_active and obj_section.is_deleted:
                obj_section.is_deleted = False
                obj_section.save()
            elif not is_active and not obj_section.is_deleted:
                obj_section.is_deleted = True
                obj_section.save()

    def get_inventory(self, cart=None):
        query_set_inventory = Inventories.objects.filter(product=self)
        inventory = 0
        for element in query_set_inventory:
            inventory += element.quantity
        if cart:
            quantity = cart.get_quantity_product(self.guid)
            if type(quantity) == int:
                inventory = max(inventory - quantity, 0)
        return inventory

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
        else:
            query_set_price = Prices.objects.filter(product=self)
            if len(query_set_price):
                currency = query_set_price[0].currency
                currency_name = query_set_price[0].currency.name
                currency_id = query_set_price[0].currency.id
                price = query_set_price[0].value
                price_ruble = currency.change_ruble(price)
                return dict(price=price, price_ruble=price_ruble, currency_name=currency_name, currency_id=currency_id)
        return dict(price=0, price_ruble=0, currency_name='', currency_id=0)


class Store(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
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
        currency = cache.get('ruble_currency_id')
        if currency is not None:
            return currency
        try:
            currency = Currency.objects.get(code='643')
        except Currency.DoesNotExist:
            return
        cache.set('ruble_currency_id', currency.id, 3600)
        return currency.id

    def get_today_course(self):
        json_str = cache.get('today_course_ruble')
        if json_str is not None:
            try:
                return json.loads(json_str)
            except TypeError:
                pass
        from django.db.models import Max
        dict_max_date = Courses.objects.filter(currency=self).aggregate(max_date=Max('date'))
        if not dict_max_date['max_date'] is None:
            set_course = Courses.objects.filter(currency=self).filter(date=dict_max_date['max_date'])
            if len(set_course) > 0:
                cache.set('today_course_ruble',
                          json.dumps(
                              {'course': set_course[0].course,
                               'multiplicity': set_course[0].multiplicity}
                          ), 3600)
                return {'course': set_course[0].course, 'multiplicity': set_course[0].multiplicity}
        cache.set('today_course_ruble', json.dumps({'course': 1, 'multiplicity': 1}), 3600)
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


class CustomersFiles(models.Model):
    customer = models.ForeignKey(Customer, db_index=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, default='')
    view = models.CharField(max_length=150, default='')
    url = models.CharField(max_length=250, default='')
    change_date = models.DateTimeField(default=timezone.now)
    type_file = models.CharField(max_length=5, default='')


class Courses(models.Model):
    date = models.DateField(db_index=True)
    currency = models.ForeignKey(Currency, db_index=True, on_delete=models.PROTECT)
    course = models.FloatField(default=0)
    multiplicity = models.IntegerField(default=1)


class Order(models.Model):
    PAYMENT_FORM = (('Наличные', 'Наличные'), ('Безналичные', 'Безналичные'))
    SHIPMENT_TYPE = (('Самовывоз', 'Самовывоз'), ('Доставка', 'Доставка'))
    STATUS_ORDER = (('Новый', 'Новый'), ('ВОбработке', 'В обработке'), ('Выполнен', 'Выполнен'), ('Отменен', 'Отменен'))

    date = models.DateTimeField(auto_now_add=True, db_index=True)
    person = models.ForeignKey(Person, db_index=True, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, db_index=True, on_delete=models.PROTECT, null=True)
    guid = models.CharField(max_length=50, db_index=True, default='')
    updated = models.DateTimeField(auto_now=True)
    delivery = models.DateTimeField(null=True)
    shipment = models.CharField(max_length=50, choices=SHIPMENT_TYPE, null=True)
    payment = models.CharField(max_length=50, choices=PAYMENT_FORM, null=True)
    status = models.CharField(max_length=50, choices=STATUS_ORDER, default=STATUS_ORDER[0][1])
    comment = models.TextField(null=True)

    class RequestOrderError(BaseException):
        pass

    class LockOrderError(BaseException):
        pass

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def __iter__(self):
        number = 0
        for item in self.items.all():
            number += 1
            dict_ = dict(
                number=number,
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
    def get_current_filters(request):
        json_str = request.session.get('get_current_filters')
        try:
            return json.loads(json_str, object_hook=date_hook)
        except TypeError:
            end_date = datetime.date.today()
            begin_date = datetime.date(day=end_date.day, month=end_date.month - 1, year=end_date.year)
            return dict(begin_date=begin_date, end_date=end_date)

    @staticmethod
    def add_current_session(request, begin_date=None, end_date=None):
        request.session['get_current_filters'] = json.dumps(
            dict(begin_date=begin_date, end_date=end_date))
        request.session.set_expiry(86400)
        request.session.modified = True

    @staticmethod
    def get_orders_list(user, begin_date=None, end_date=None):
        set_person = Person.objects.filter(user=user)
        if len(set_person) == 0:
            return []
        orders = Order.objects.filter(person=set_person[0])
        if begin_date and end_date:
            try:
                begin_datetime = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0) \
                    .astimezone(tz=pytz.timezone(settings.TIME_ZONE))
                end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59) \
                    .astimezone(tz=pytz.timezone(settings.TIME_ZONE))
                orders = orders.filter(date__range=(begin_datetime, end_datetime)).order_by('-date')
            except AttributeError:
                pass
        return orders

    def get_json_for_request(self):
        if self.customer:
            customer = self.customer.guid
        else:
            customer = self.person.customer.guid
        rest = dict(guid=self.guid,
                    date=self.date,
                    number=self.id,
                    customer=customer,
                    person=self.person.guid,
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

    @classmethod
    def orders_request(cls):
        orders = cls.objects.filter(guid='')
        for obj in orders:
            try:
                obj.request_order()
            except cls.RequestOrderError:
                pass

    def request_order(self):

        api_url = settings.API_URL + r'Order/OrderCreate/'
        data = self.get_json_for_request()
        params = {
            'Content-Type': 'application/json'}

        try:
            answer = requests.post(api_url, data=data, headers=params)
        except requests.exceptions.ConnectionError:
            raise self.RequestOrderError

        if answer.status_code != 200:
            pass

        try:
            dict_obj = answer.json()
        except json.decoder.JSONDecodeError:
            raise self.RequestOrderError

        if dict_obj.get('success', None) is None:
            raise self.RequestOrderError

        result = dict_obj.get('result', None)
        if result is None:
            raise self.RequestOrderError
        if len(result) == 0:
            raise self.RequestOrderError()
        if result[0]['number'] != self.id:
            raise self.RequestOrderError

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
    customer = cache.get(f'user_customer{user.id}')
    if customer is not None:
        return customer
    try:
        person = user.person
    except Person.DoesNotExist:
        return
    customer = person.customer
    cache.set(f'user_customer{user.id}', customer)
    return customer


def get_person(user):
    try:
        person = user.person
    except Person.DoesNotExist:
        return
    return person
