from rest_framework import serializers

from san_site.models import Product


class ProductSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField(method_name='calculate_article')
    article_brand = serializers.SerializerMethodField(method_name='calculate_article_brand')
    quantity = serializers.SerializerMethodField(method_name='calculate_quantity')
    brand = serializers.SerializerMethodField(method_name='calculate_brand')
    price = serializers.SerializerMethodField(method_name='calculate_price')
    currency = serializers.SerializerMethodField(method_name='calculate_currency')
    rrp = serializers.SerializerMethodField(method_name='calculate_rrp')

    class Meta:
        model = Product
        fields = (
            'article', 'name', 'brand', 'article_brand', 'barcode', 'matrix', 'image', 'quantity', 'price',
            'currency', 'rrp')

    @staticmethod
    def calculate_article(instance):
        return instance.code

    @staticmethod
    def calculate_article_brand(instance):
        return instance.code_brand

    @staticmethod
    def calculate_brand(instance):
        return instance.brand_name

    @staticmethod
    def calculate_quantity(instance):
        return '>10' if instance.quantity > 10 else instance.quantity

    @staticmethod
    def calculate_price(instance):
        return instance.price

    @staticmethod
    def calculate_currency(instance):
        return instance.currency

    @staticmethod
    def calculate_rrp(instance):
        return instance.price_rrp
