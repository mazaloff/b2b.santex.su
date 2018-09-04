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
                                     'price': product.price}
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
            self.cart[str(product.guid)]['code'] = product.code
            self.cart[str(product.guid)]['name'] = product.name

        for item in self.cart.values():
            item['price'] = item['price']
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return len(self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_cart_list(self):

        list_res_ = []

        for element in self:
            list_res_.append({'code': element['code'],
                              'name': element['name'],
                              'quantity': element['quantity'],
                              'price': element['price'],
                              'total_price': element['total_price'],
                              })

        return list_res_

    @property
    def cart_height(self):
        len_ = len(self)
        if len_ == 0:
            return 0
        else:
            return min(len_ * 34, 34 * 6)
