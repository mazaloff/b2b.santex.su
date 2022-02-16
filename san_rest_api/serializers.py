import datetime
import json

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import resolve_url
from rest_framework import serializers
import base64, uuid
from django.core.files.base import ContentFile

from san_site.models import Product, Currency, Order, OrderItem, Bill


class ProductSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField(method_name='calculate_code')
    article = serializers.SerializerMethodField(method_name='calculate_article')
    barcode = serializers.SerializerMethodField(method_name='calculate_barcode')
    name = serializers.SerializerMethodField(method_name='calculate_name')
    matrix = serializers.SerializerMethodField(method_name='calculate_matrix')
    quantity = serializers.SerializerMethodField(method_name='calculate_quantity')
    photo = serializers.SerializerMethodField(method_name='calculate_photo')
    brand = serializers.SerializerMethodField(method_name='calculate_brand')
    price = serializers.SerializerMethodField(method_name='calculate_price')
    currency = serializers.SerializerMethodField(method_name='calculate_currency')
    rrp = serializers.SerializerMethodField(method_name='calculate_rrp')

    class Meta:
        model = Product
        fields = (
            'code', 'name', 'brand', 'article', 'barcode', 'matrix', 'photo', 'quantity', 'price',
            'currency', 'rrp')

    @staticmethod
    def calculate_name(instance):
        return instance.name_

    @staticmethod
    def calculate_code(instance):
        return instance.code_

    @staticmethod
    def calculate_barcode(instance):
        return instance.barcode_

    @staticmethod
    def calculate_matrix(instance):
        return instance.matrix_

    @staticmethod
    def calculate_article(instance):
        return instance.article_

    @staticmethod
    def calculate_brand(instance):
        return instance.brand_name_

    @staticmethod
    def calculate_quantity(instance):
        return 10 if instance.quantity > 10 else instance.quantity

    @staticmethod
    def calculate_price(instance):
        return instance.price

    @staticmethod
    def calculate_currency(instance):
        return instance.currency

    @staticmethod
    def calculate_rrp(instance):
        return instance.price_rrp

    @staticmethod
    def calculate_photo(instance):
        return '' if instance.image.name == '' else settings.URL + resolve_url(instance.image.url)


class ProductSerializerV1(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='calculate_id')
    article = serializers.SerializerMethodField(method_name='calculate_article')
    barcode = serializers.SerializerMethodField(method_name='calculate_barcode')
    name = serializers.SerializerMethodField(method_name='calculate_name')
    matrix = serializers.SerializerMethodField(method_name='calculate_matrix')
    quantity = serializers.SerializerMethodField(method_name='calculate_quantity')
    photo = serializers.SerializerMethodField(method_name='calculate_photo')
    brand = serializers.SerializerMethodField(method_name='calculate_brand')
    price = serializers.SerializerMethodField(method_name='calculate_price')
    price_base = serializers.SerializerMethodField(method_name='calculate_price_base')
    currency = serializers.SerializerMethodField(method_name='calculate_currency')
    price_rub = serializers.SerializerMethodField(method_name='calculate_price_rub')
    rrp_rub = serializers.SerializerMethodField(method_name='calculate_rrp_rub')

    class Meta:
        model = Product
        fields = (
            'id', 'article', 'name', 'brand', 'barcode', 'matrix', 'photo', 'quantity', 'price', 'price_base',
            'currency', 'price_rub', 'rrp_rub')

    @staticmethod
    def calculate_name(instance):
        return instance.name_

    @staticmethod
    def calculate_id(instance):
        return instance.guid_

    @staticmethod
    def calculate_barcode(instance):
        return instance.barcode_

    @staticmethod
    def calculate_matrix(instance):
        return instance.matrix_

    @staticmethod
    def calculate_article(instance):
        return instance.article_

    @staticmethod
    def calculate_brand(instance):
        return instance.brand_name_

    @staticmethod
    def calculate_quantity(instance):
        return 10 if instance.quantity > 10 else instance.quantity

    @staticmethod
    def calculate_price(instance):
        return instance.price

    @staticmethod
    def calculate_price_base(instance):
        return instance.price_base

    @staticmethod
    def calculate_currency(instance):
        return 'RUB' if instance.currency.lower() == 'руб' else instance.currency.upper()

    @staticmethod
    def calculate_price_rub(instance):
        courses = get_currency()
        course = courses.get(str(instance.currency_id), {'course': 1, 'multiplicity': 1})
        return round(instance.price * course['course'] / course['multiplicity'], 2)

    @staticmethod
    def calculate_rrp_rub(instance):
        return instance.price_rrp

    @staticmethod
    def calculate_photo(instance):
        return '' if instance.image.name == '' else settings.URL + resolve_url(instance.image.url)


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    guid = serializers.CharField()
    date = serializers.DateTimeField()
    customer = serializers.SerializerMethodField(method_name='customer_guid')
    person = serializers.SerializerMethodField(method_name='person_guid')
    shipment = serializers.CharField()
    payment = serializers.CharField()
    delivery = serializers.DateTimeField()
    status = serializers.CharField()
    receiver_bills = serializers.CharField()
    comment = serializers.CharField()
    items = serializers.SerializerMethodField(method_name='get_items')

    class Meta:
        model = Order
        fields = (
            'id', 'guid', 'date', 'customer', 'person', 'shipment', 'payment', 'delivery', 'status', 'receiver_bills',
            'comment', 'items')

    @staticmethod
    def customer_guid(instance):
        return instance.customer.guid

    @staticmethod
    def person_guid(instance):
        return instance.person.guid

    @staticmethod
    def get_items(instance):
        return OrderItemSerializer(OrderItem.objects.filter(order_id=instance.id).all(), many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(method_name='product_guid')
    quantity = serializers.IntegerField()
    price = serializers.FloatField()
    currency = serializers.SerializerMethodField(method_name='currency_code')
    price_ruble = serializers.FloatField()

    class Meta:
        model = OrderItem
        fields = (
            'product', 'quantity', 'price', 'currency', 'price_ruble')

    @staticmethod
    def product_guid(instance):
        return instance.product.guid

    @staticmethod
    def currency_code(instance):
        value = Currency.objects.get(id=instance.currency_id)
        return value.code


# Custom image field - handles base 64 encoded images
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,') # format ~= data:image/X,
            ext = format.split('/')[-1] # guess file extension
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name=id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class BillSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    guid = serializers.CharField()
    date = serializers.DateTimeField()
    order = serializers.SerializerMethodField(method_name='order_id')
    customer = serializers.SerializerMethodField(method_name='customer_guid')
    person = serializers.SerializerMethodField(method_name='person_guid')
    comment = serializers.CharField()
    total = serializers.DecimalField(15, 2)
    file = Base64ImageField()

    class Meta:
        model = Order
        fields = (
            'id', 'guid', 'date', 'order', 'customer', 'person', 'comment', 'total', 'file')

    @staticmethod
    def customer_guid(instance):
        return instance.customer.guid

    @staticmethod
    def person_guid(instance):
        return instance.person.guid

    @staticmethod
    def order_id(instance):
        return instance.order.id


def get_currency():
    json_str = cache.get(f'api_currency{str(datetime.date.today())}')
    if json_str is not None:
        try:
            value = json.loads(json_str)
            if isinstance(json.loads(json_str), dict):
                return value
        except TypeError:
            pass
    courses = {}
    currency = Currency.objects.all()
    for elem in currency:
        courses[str(elem.id)] = elem.get_today_course(True)
    cache.set(f'api_currency{str(datetime.date.today())}',
              json.dumps(courses), 7200)
    return courses
