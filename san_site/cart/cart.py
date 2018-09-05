from django.conf import settings
from san_site.models import Product


class Cart(object):

    def __init__(self, request):
        self.session = request.session
        self.user = request.user
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_guid = str(product.guid)
        if product_guid not in self.cart:
            dict_price = product.get_price(self.user)
            self.cart[product_guid] = {'quantity': 0,
                                    'price': dict_price['price'],
                                    'currency': dict_price['currency'],
                                    'price_ruble': dict_price['price_ruble']}
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
            self.cart[str(product.guid)]['guid'] = product.guid

        for item in self.cart.values():
            item['total_price'] = round(item['price'] * item['quantity'], 2)
            item['total_price_ruble'] = round(item['price_ruble'] * item['quantity'], 2)
            yield item

    def __len__(self):
        return len(self.cart.values())

    def get_total_price(self):
        return round(sum(item['total_price_ruble'] for item in self.cart.values()), 2)

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_cart_list(self):
        list_res_ = []
        for element in self:
            list_res_.append(self.get_tr_cart(element['guid']))
        return list_res_

    def get_tr_cart(self, product_guid):
        if product_guid not in self.cart:
            return
        element = self.cart[product_guid]

        if 'guid' not in element.keys():
            try:
                product = Product.objects.get(guid=product_guid)
            except Product.DoesNotExist:
                return

            element['code'] = product.code
            element['name'] = product.name
            element['guid'] = product.guid
        element['total_price'] = round(element['price'] * element['quantity'], 2)
        element['total_price_ruble'] = round(element['price_ruble'] * element['quantity'], 2)

        return {'guid': element['guid'],
                'code': element['code'],
                'name': element['name'],
                'quantity': element['quantity'],
                'price': element['price'],
                'currency': element['currency'],
                'total_price': element['total_price'],
                'total_price_ruble': element['total_price_ruble'],
                'url_add_quantity': 'cart/add_quantity/?product=' + element['guid'],
                'url_reduce_quantity': 'cart/reduce_quantity/?product=' + element['guid'],
                'url_tr_cart': 'tr_cart' + element['guid'],
                'url_td_cart_quantity': 'td_cart_quantity' + element['guid'],
                'url_td_cart_total_price': 'td_cart_total_price' + element['guid'],
                'url_td_cart_total_price_ruble': 'td_cart_total_price_ruble' + element['guid']
                }

    @property
    def cart_height(self):
        len_ = len(self)
        if len_ == 0:
            return 0
        else:
            return min(len_ * 34, 34 * 6)
