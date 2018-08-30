from django.db import models
from django.utils import timezone


class Section(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField()
    parent_guid = models.CharField(max_length=50, db_index=True)
    created_date = models.DateTimeField(
            default=timezone.now)
    is_deleted = models.BooleanField()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


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
