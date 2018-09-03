from django.conf import settings
from san_site.models import Product
from decimal import Decimal


class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_guid = str(product.guid)
        if product_guid not in self.cart:
            self.cart[product_guid] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_guid]['quantity'] = quantity
        else:
            self.cart[product_guid]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_guid = str(product.guid)
        if product_guid in self.cart:
            del self.cart[product_guid]
            self.save()

    def __iter__(self):
        product_guids = self.cart.keys()
        products = Product.objects.filter(guid__in=product_guids)
        for product in products:
            self.cart[str(product.guid)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
