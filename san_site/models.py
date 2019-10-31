import datetime
import json
import re

import pytz
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import connection
from django.db import models
from django.db.models.query import Prefetch
from django.shortcuts import loader
from django.utils import timezone
from django.utils.safestring import mark_safe

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
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    allow_order = models.BooleanField(default=False)
    key = models.CharField(max_length=20, default='xxx')
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
                'url': url + '/' + new_key + '/'
            }
        )
        text_content = 'This is an important message.'
        msg = EmailMultiAlternatives(
            "Информация для доступа к сайту Santex.b2b-commerce",
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


class Brand(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    group = models.ForeignKey('self', db_index=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)
    is_inventories = models.BooleanField(default=True, db_index=True)

    objects = SectionManager()

    def __str__(self):
        return self.name

    @staticmethod
    def change_is_inventories():
        sections = Section.objects.all()
        for obj_section in sections:
            is_active = len(obj_section.get_goods_list_section(only_stock=True)) > 0
            if is_active and not obj_section.is_inventories:
                obj_section.is_inventories = True
                obj_section.save()
            elif not is_active and obj_section.is_inventories:
                obj_section.is_inventories = False
                obj_section.save()

    @staticmethod
    def change_is_deleted():
        sections = Section.objects.all()
        for obj_section in sections:
            is_active = len(obj_section.get_goods_list_section(only_available=True)) > 0
            if is_active and obj_section.is_deleted:
                obj_section.is_deleted = False
                obj_section.save()
            elif not is_active and not obj_section.is_deleted:
                obj_section.is_deleted = True
                obj_section.save()

    def list_with_children(self):
        result = Section.objects.raw("""
            WITH RECURSIVE Bfs AS (
              SELECT section.id       AS id,
                     section.name     AS name,
                     section.group_id AS group_id,
                     0                AS level
              FROM san_site_section AS section
              WHERE section.id = %s
              UNION ALL
              SELECT section.id       AS id,
                     section.name     AS name,
                     section.group_id AS group_id,
                     Bfs.level + 1    AS level
              FROM san_site_section AS section
                     JOIN Bfs ON section.group_id = Bfs.id AND section.is_deleted = FALSE
            )
            SELECT Bfs.id                    AS id,
                   Bfs.name                  AS name,
                   COALESCE(Bfs.group_id, 0) AS group_id,
                   Bfs.level                 AS level
            FROM Bfs
            ORDER BY Bfs.level, Bfs.name;
            """, [self.id, ])

        list_sections = []
        for value in result:
            list_sections.append(value)
        return list_sections

    def add_current_session(self, request):
        request.session['id_current_session'] = self.id
        request.session.set_expiry(86400)
        request.session.modified = True

    @property
    def full_name(self):
        parents_name = self.__create_parents_name()
        return parents_name + ('' if parents_name == '' else '/') + self.name

    def __create_parents_name(self, full_name=''):
        parent = self.group
        if parent or None:
            full_name = parent.name + ('' if full_name == '' else '/') + full_name
            full_name = parent.__create_parents_name(full_name)
        return full_name

    @staticmethod
    def get_current_session(request):
        return request.session.get('id_current_session')

    @staticmethod
    def get_data_for_tree(only_stock):
        data = []
        with connection.cursor() as cursor:
            cursor.execute("""
            WITH RECURSIVE Bfs AS (
              SELECT section.id       AS id,
                     section.name     AS name,
                     section.group_id AS group_id,
                     0                AS level
              FROM san_site_section AS section
              WHERE section.group_id ISNULL
                AND section.is_deleted = FALSE
                AND (%s = FALSE OR section.is_inventories = TRUE)
              UNION ALL
              SELECT section.id       AS id,
                     section.name     AS name,
                     section.group_id AS group_id,
                     Bfs.level + 1    AS level
              FROM san_site_section AS section
                     JOIN Bfs ON section.group_id = Bfs.id
                      AND section.is_deleted = FALSE
                      AND (%s = FALSE OR section.is_inventories = TRUE)
            )
            SELECT Bfs.id                    AS id,
                   Bfs.name                  AS name,
                   COALESCE(Bfs.group_id, 0) AS group_id,
                   Bfs.level                 AS level
            FROM Bfs
            ORDER BY Bfs.level, Bfs.name;
            """, [only_stock, only_stock])
            rows = cursor.fetchall()
            for row in rows:
                data.append({'id': row[0], 'parent': '#' if row[2] == 0 else row[2], 'text': row[1], 'href': row[0]})
        return data

    @staticmethod
    def get_goods_list(**kwargs):
        return Section.__get_goods_list_raw(kwargs)

    @staticmethod
    def get_goods_list_with_kwargs(**kwargs):
        goods_list = Section.__get_goods_list_raw(kwargs)
        return goods_list, kwargs

    @staticmethod
    def __get_goods_list_raw(kwargs):

        user = kwargs.get('user', None)
        id_section = kwargs.get('id_section', 0)
        search = kwargs.get('search', '')
        search = search.replace('\\', '')

        only_stock = kwargs.get('only_stock', False)
        only_promo = kwargs.get('only_promo', False)
        only_available = kwargs.get('only_available', True)

        is_price_rrp = kwargs.get('is_price_rrp', False)

        list_res_ = []

        param = []

        current_customer = get_customer(user)
        current_customer_id = 0
        if current_customer:
            current_customer_id = current_customer.id

        select_request_section = ''
        join_request_section = ''
        where_request_section = ' TRUE '
        if id_section != 0:
            param.append(id_section)

            select_request_section = """
            RECURSIVE Bfs AS (
              SELECT section.id AS id
              FROM san_site_section AS section
              WHERE section.id = %s
              UNION ALL
              SELECT section.id AS id
              FROM san_site_section AS section
                     JOIN Bfs ON section.group_id = Bfs.id AND section.is_deleted = FALSE
            ),"""
            join_request_section = 'JOIN Bfs ON _product.section_id = Bfs.id'
            where_request_section = '_product.section_id IN (SELECT Bfs.id FROM Bfs)'

        where_request_search = 'TRUE'
        field_sort_search = "0"
        if search != '':
            field_sort_search = '''MIN(CASE 
                                        WHEN UPPER(_product.code::text) LIKE UPPER(%s) THEN 1
                                        WHEN UPPER(_product.name::text) LIKE UPPER(%s) THEN 2
                                        ELSE 0 
                                    END)
                                    '''
            where_request_search = """(UPPER(_product.code::text) LIKE UPPER(%s)
                                        OR UPPER(_product.name::text) LIKE UPPER(%s))"""
            param += [f'{search}%', f'%{search}%']

        param += [current_customer_id, only_available]

        if search != '':
            param += [f'{search}%', f'%{search}%']

        param += [only_promo, only_stock]

        with connection.cursor() as cursor:
            cursor.execute(
                f""" WITH {select_request_section} result AS (
                    SELECT _product.id AS id,
                        _product.code AS code,
                        _product.name AS name,
                        _product.guid AS guid,
                        _product.matrix AS matrix,
                        CASE WHEN _product.image = '' THEN ''
                            ELSE 'media/' || _product.image 
                            END AS image,
                        _product.is_deleted AS is_deleted,
                        COALESCE(_prices.value, 0) AS price,
                        COALESCE(_prices_cur.name, '') AS price_currency,
                        COALESCE(_customersprices.percent, 0) AS percent,
                        COALESCE(_customersprices.discount, COALESCE(_prices.value, 0)) AS discount,
                        COALESCE(_prices.rrp, 0) AS price_rrp,
                        COALESCE(_customersprices.promo, FALSE) AS promo,
                        COALESCE(_customersprices_cur.id, COALESCE(_prices_cur.id, 0)) AS currency_id,
                        COALESCE(_customersprices_cur.name, COALESCE(_prices_cur.name, '')) AS currency,
                        SUM(COALESCE(_inventories.quantity, 0)) AS quantity,
                        {field_sort_search} AS sort_search
                    FROM san_site_product _product
                         {join_request_section}
                         LEFT JOIN san_site_prices _prices ON _product.id = _prices.product_id
                            LEFT JOIN san_site_currency _prices_cur ON _prices.currency_id = _prices_cur.id
                         LEFT JOIN san_site_customersprices _customersprices 
                            ON _customersprices.customer_id = %s AND _product.id = _customersprices.product_id  
                                LEFT JOIN san_site_currency _customersprices_cur 
                                    ON _customersprices.currency_id = _customersprices_cur.id   
                         LEFT JOIN san_site_inventories _inventories ON _product.id = _inventories.product_id
                    WHERE (%s = FALSE OR _product.is_deleted = FALSE)
                        AND {where_request_section}
                        AND {where_request_search}
                        AND (%s = FALSE OR COALESCE (_customersprices.promo, FALSE) = TRUE)
                        AND (%s = FALSE OR COALESCE(_inventories.quantity, 0) > 0)        
                    GROUP BY _product.id,
                        _product.code,
                        _product.name,
                        _product.guid,
                        _product.matrix,
                        _product.is_deleted,
                        COALESCE(_prices.value, 0),
                        COALESCE(_prices_cur.name, ''),
                        COALESCE(_customersprices.percent, 0),
                        COALESCE(_customersprices.discount, COALESCE(_prices.value, 0)),
                        COALESCE(_prices.rrp, 0),
                        COALESCE(_customersprices.promo, FALSE),
                        COALESCE(_customersprices_cur.id, COALESCE(_prices_cur.id, 0)),
                        COALESCE(_customersprices_cur.name, COALESCE(_prices_cur.name, ''))
                    )
                    SELECT *
                    FROM result
                    ORDER BY sort_search, result.code;
                """, param
            )

            rows = cursor.fetchall()
            flag = (0 if search.isdigit() else re.IGNORECASE)

            for row in rows:

                sel_row = SelectRow(*row)
                quantity = '>10' if row[15] > 10 else '' if row[15] == 0 else row[15]

                if search != '':
                    match = re.search(search, sel_row.code, flags=flag)
                    sel_row_code = sel_row.code if match is None else mark_safe(sel_row.code.replace(
                        match[0], f'<span class="search">{match[0]}</span>'
                    ))
                    match = re.search(search, sel_row.name, flags=flag)
                    sel_row_name = sel_row.name if match is None else mark_safe(sel_row.name.replace(
                        match[0], f'<span class="search">{match[0]}</span>'
                    ))
                else:
                    sel_row_code = sel_row.code
                    sel_row_name = sel_row.name

                if not is_price_rrp:
                    is_price_rrp = False if sel_row.price_rrp == 0 or sel_row.price_rrp == 0.01 else True
                list_res_.append({
                    'product': sel_row,
                    'guid': sel_row.guid,
                    'code': sel_row_code,
                    'name': sel_row_name,
                    'image': sel_row.image,
                    'is_image': (sel_row.image != ""),
                    'relevant': sel_row.matrix in Product.RELEVANT_MATRIX,
                    'quantity': quantity,
                    'price': '' if sel_row.price == 0 or sel_row.price == 0.01 else sel_row.price,
                    'price_currency': sel_row.price_currency,
                    'price_rrp': '' if sel_row.price_rrp == 0 or sel_row.price_rrp == 0.01 else sel_row.price_rrp,
                    'promo': sel_row.promo,
                    'discount': '' if sel_row.discount == 0 else sel_row.discount,
                    'currency': sel_row.currency,
                    'currency_id': sel_row.currency_id,
                    'percent': '' if sel_row.percent == 0 else sel_row.percent}
                )

        if 'is_price_rrp' in kwargs.keys():
            kwargs['is_price_rrp'] = is_price_rrp

        return list_res_

    def get_goods_list_section(self, **kwargs):
        kwargs['id_section'] = self.id
        return Section.get_goods_list(**kwargs)

    def get_goods_list_section_with_kwargs(self, **kwargs):
        kwargs['id_section'] = self.id
        return Section.get_goods_list_with_kwargs(**kwargs)


class Product(models.Model):
    RELEVANT_MATRIX = ('Акция', 'Заказной', 'Основной')

    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=30, db_index=True)
    code_brand = models.CharField(max_length=50, default='')
    section = models.ForeignKey(Section, db_index=True, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, null=True, on_delete=models.PROTECT)
    matrix = models.CharField(max_length=30, default='Основной')
    barcode = models.CharField(max_length=30, default='')
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)
    image = models.ImageField(upload_to='photos', default='', blank=True)

    def __str__(self):
        return self.name

    def is_relevant(self):
        return self.matrix in Product.RELEVANT_MATRIX

    @property
    def is_image(self):
        return self.image.name != ''

    @property
    def inventories(self):
        result = {}
        query_set_inventory = Inventories.objects.filter(product=self).select_related('store')
        for element in query_set_inventory:
            quantity = '>10' if element.quantity > 10 else element.quantity
            result.update(dict([(element.store.short_name, quantity)]))
        return result

    @classmethod
    def change_relevant_products(cls):

        sections = Section.objects.filter(group__isnull=True)
        for obj_section in sections:
            goods_list = obj_section.get_goods_list_section(only_available=False)
            filter_guid = [element_list['guid'] for element_list in goods_list]
            filter_object = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}
            for element_list in goods_list:
                raw = element_list['product']
                if not raw.is_deleted:
                    if element_list['quantity'] == '' and element_list['price'] == '':
                        cur_object = filter_object.get(element_list['guid'], None)
                        if cur_object:
                            cur_object.is_deleted = True
                            cur_object.save()
                    elif element_list['quantity'] == '' and not element_list['relevant']:
                        cur_object = filter_object.get(element_list['guid'], None)
                        if cur_object:
                            cur_object.is_deleted = True
                            cur_object.save()
                elif element_list['relevant']:
                    if element_list['quantity'] != '' or element_list['price'] != '':
                        cur_object = filter_object.get(element_list['guid'], None)
                        if cur_object:
                            cur_object.is_deleted = False
                            cur_object.save()
                else:
                    if element_list['quantity'] != '':
                        cur_object = filter_object.get(element_list['guid'], None)
                        if cur_object:
                            cur_object.is_deleted = True
                            cur_object.save()

        Section.change_is_deleted()
        Section.change_is_inventories()

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
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Price(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Currency(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
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

    def get_today_course(self, update_cache=False):
        json_str = cache.get(f'today_course_{self.id}')
        if json_str is not None and not update_cache:
            try:
                return json.loads(json_str)
            except TypeError:
                pass
        from django.db.models import Max
        dict_max_date = Courses.objects.filter(currency=self).aggregate(max_date=Max('date'))
        if not dict_max_date['max_date'] is None:
            set_course = Courses.objects.filter(currency=self).filter(date=dict_max_date['max_date'])
            if len(set_course) > 0:
                cache.set(f'today_course_{self.id}',
                          json.dumps(
                              {'course': set_course[0].course,
                               'multiplicity': set_course[0].multiplicity}
                          ), 3600)
                return {'course': set_course[0].course, 'multiplicity': set_course[0].multiplicity}
        cache.set(f'today_course_{self.id}', json.dumps({'course': 1, 'multiplicity': 1}), 3600)
        return {'course': 1, 'multiplicity': 1}

    def change_ruble(self, value):
        course = self.get_today_course()
        return round(value * course['course'] / course['multiplicity'], 2)

    def recalculation(self, to, value):
        if to is not None:
            return value
        course_from = self.get_today_course()
        course_to = to.get_today_course()
        return round((value * course_from['course'] / course_to['multiplicity']) /
                     (course_to['course'] * course_from['multiplicity']), 2)


class Inventories(models.Model):
    product = models.ForeignKey(Product, db_index=True, on_delete=models.PROTECT)
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)


class Prices(models.Model):
    product = models.ForeignKey(Product, db_index=True, on_delete=models.PROTECT)
    price = models.ForeignKey(Price, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, db_index=False)
    value = models.FloatField(default=0)
    rrp = models.FloatField(default=0)


class PricesSale(models.Model):
    product = models.ForeignKey(Product, related_name='product_prices_sale',
                                db_index=True, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    value = models.FloatField(default=0)


class CustomersPrices(models.Model):
    product = models.ForeignKey(Product, db_index=False, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, db_index=False, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, db_index=False)
    discount = models.FloatField(default=0)
    percent = models.FloatField(default=0)
    promo = models.BooleanField(default=False)

    class Meta:
        unique_together = (("product", "customer"),)


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
    receiver_bills = models.CharField(max_length=50, default='')

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

    @property
    def bills(self):
        list_bills = []
        query_set = Bill.objects.filter(order=self)
        query_set.select_related('currency')
        for el in query_set:
            url = f'\\files\\static\\bills\\{el.guid}'
            list_bills.append(dict(number=el.number,
                                   date=el.date,
                                   total=el.total,
                                   currency=el.currency.name,
                                   url=url))
        return list_bills

    @staticmethod
    def get_current_filters(request):
        json_str = request.session.get('get_current_filters')
        try:
            load_dict = json.loads(json_str, object_hook=date_hook)
            # End date of the period is always today
            load_dict['end_date'] = datetime.date.today()
            return load_dict
        except TypeError:
            end_date = datetime.date.today()
            begin_date = end_date - datetime.timedelta(days=60)
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
                orders = orders.filter(date__range=(begin_datetime, end_datetime))
            except AttributeError:
                pass
        orders = orders.select_related('customer').prefetch_related(
            Prefetch("order_bills", Bill.objects.filter(person=set_person[0]))
        ).order_by('-date')
        result_list = []
        for elem in orders:
            is_bill = False
            for _ in elem.order_bills.all():
                is_bill = True
                break

            result_list.append(dict(guid=elem.guid,
                                    id=elem.id,
                                    date=elem.date,
                                    customer=elem.customer,
                                    get_total_cost=elem.get_total_cost,
                                    shipment=elem.shipment,
                                    delivery=elem.delivery,
                                    status=elem.status,
                                    comment=elem.comment,
                                    is_bill=is_bill))
        return result_list

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
                    receiver_bills=self.receiver_bills,
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
            answer = requests.post(api_url, data=data, headers=params, timeout=60)
        except requests.exceptions.RequestException:
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
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=Currency.get_ruble)
    price_ruble = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return round(self.price_ruble * self.quantity, 2)


class Bill(models.Model):
    date = models.DateTimeField(db_index=True)
    number = models.CharField(max_length=15, default='')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='order_bills')
    person = models.ForeignKey(Person, db_index=True, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, db_index=True, on_delete=models.PROTECT, null=True)
    guid = models.CharField(max_length=50, db_index=True, default='')
    updated = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, db_index=False)
    comment = models.TextField(null=True)
    file = models.FileField(upload_to='bills', default='', blank=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return 'Order {}'.format(self.id)


def get_customer(user):
    if user is None:
        return user
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
    if user is None:
        return user
    try:
        person = user.person
    except Person.DoesNotExist:
        return
    return person


class SelectRow:
    def __init__(self, id, code, name, guid, matrix, image, is_deleted, price, price_currency, percent, discount,
                 price_rrp, promo,
                 currency_id, currency, quantity, sort_search):
        self.id: int = id
        self.code: str = code
        self.name: str = name
        self.guid: str = guid
        self.matrix: str = matrix
        self.image: str = image
        self.is_deleted: bool = is_deleted
        self.price: float = price
        self.price_currency: str = price_currency
        self.percent: float = percent
        self.discount: float = discount
        self.price_rrp: float = price_rrp
        self.promo: bool = promo
        self.currency_id: int = currency_id
        self.currency: str = currency
        self.quantity: int = quantity
