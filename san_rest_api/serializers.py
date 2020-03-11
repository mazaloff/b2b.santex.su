from django.shortcuts import resolve_url
from django.conf import settings

from rest_framework import serializers

from san_site.models import Product, Currency

courses = {}
currency = Currency.objects.all()
for elem in currency:
    courses[elem.id] = elem.get_today_course()


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
        course = courses.get(instance.currency_id, {'course': 1, 'multiplicity': 1})
        return round(instance.price * course['course'] / course['multiplicity'], 2)

    @staticmethod
    def calculate_rrp_rub(instance):
        return instance.price_rrp

    @staticmethod
    def calculate_photo(instance):
        return '' if instance.image.name == '' else settings.URL + resolve_url(instance.image.url)
