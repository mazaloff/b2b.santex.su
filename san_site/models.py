from django.db import models
from django.utils import timezone


class SectionManager(models.Manager):
    pass


class Section(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField()
    parent_guid = models.CharField(max_length=50, db_index=True)
    created_date = models.DateTimeField(
            default=timezone.now)
    is_deleted = models.BooleanField()

    objects = SectionManager()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    def list_with_children(self, list_sections):
        list_sections.append(self)
        children = Section.objects.filter(parent_guid=self.guid)
        for child in children:
            list_sections.append(child)
            child.list_with_children(list_sections)

    def get_goods_list(self):

        list_sections = []
        self.list_with_children(list_sections)

        products = Product.objects.filter(section__in=list_sections).order_by('code') \
            .prefetch_related('product_inventories', 'product_prices')
        currencis_dict = {elem_.id: elem_.name for elem_ in Currency.objects.all()}

        list_res = []
        for value_product in products:
            quantity_sum = 0
            for product_inventories in value_product.product_inventories.all():
                quantity_sum += product_inventories.quantity
            price_value = 0
            currency_name = ''
            for product_prices in value_product.product_prices.all():
                price_value = product_prices.value
                currency_name = currencis_dict.get(product_prices.currency_id, '')
            list_res.append({'code': value_product.code,
                             'name': value_product.name,
                             'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                             'price': '' if price_value == 0 else price_value,
                             'currency': currency_name})

        return list_res


class Product(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    sort = models.IntegerField()
    section = models.ForeignKey(Section, null=True, on_delete=models.PROTECT)
    created_date = models.DateTimeField(
            default=timezone.now)
    is_deleted = models.BooleanField()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Store(models.Model):
    guid = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    sort = models.IntegerField()
    created_date = models.DateTimeField(
            default=timezone.now)
    is_deleted = models.BooleanField()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Price(models.Model):
    guid = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    sort = models.IntegerField()
    created_date = models.DateTimeField(
            default=timezone.now)
    is_deleted = models.BooleanField()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Currency(models.Model):
    guid = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    sort = models.IntegerField()
    created_date = models.DateTimeField(
            default=timezone.now)
    is_deleted = models.BooleanField()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Inventories(models.Model):
    product = models.ForeignKey(Product, related_name='product_inventories', null=True, unique=False, on_delete=models.DO_NOTHING)
    store = models.ForeignKey(Store, null=True, unique=False, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(null=False)


class Prices(models.Model):
    product = models.ForeignKey(Product, related_name='product_prices', null=True, unique=False, on_delete=models.DO_NOTHING)
    price = models.ForeignKey(Price, null=True, unique=False, on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, null=True, unique=False, on_delete=models.DO_NOTHING)
    value = models.FloatField(null=False)
