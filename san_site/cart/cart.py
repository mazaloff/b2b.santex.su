from datetime import date

from django.conf import settings
from san_site.models import Product, Currency
import datetime

class Cart(object):

    def __init__(self, request):
        self.session = request.session
        self.user = request.user
        self.price_exchange = False
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_guid = str(product.guid)
        if product_guid not in self.cart:
            dict_price = product.get_price(self.user)
            self.cart[product_guid] = {
                'date': datetime.datetime.now().date().isoformat(),
                'quantity': 0,
                'price': dict_price['price'],
                'currency_id': dict_price['currency_id'],
                'currency_name': dict_price['currency_name'],
                'price_ruble': dict_price['price_ruble']
            }
        if update_quantity:
            self.cart[product_guid]['quantity'] = quantity
        else:
            self.cart[product_guid]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
        self.price_exchange = False

    def remove(self, product):
        product_guid = str(product.guid)
        if product_guid in self.cart:
            del self.cart[product_guid]
            self.save()

    def __iter__(self):
        product_guid = self.cart.keys()
        products = Product.objects.filter(guid__in=product_guid)
        number = 0
        for product in products:
            self.cart[str(product.guid)]['product'] = product
            self.cart[str(product.guid)]['code'] = product.code
            self.cart[str(product.guid)]['name'] = product.name
            self.cart[str(product.guid)]['guid'] = product.guid

        data_now: date = datetime.datetime.now().date()

        for item in self.cart.values():
            if 'date' in item:
                if datetime.datetime.strptime(item['date'], '%Y-%m-%d').date() < data_now:
                    currency = Currency.objects.get(id=item['currency_id'])
                    item['price_ruble'] = currency.change_ruble(item['price'])
                    item['date'] = data_now.isoformat()
                    self.price_exchange = True
            number += 1
            item['total_price'] = round(item['price'] * item['quantity'], 2)
            item['total_price_ruble'] = round(item['price_ruble'] * item['quantity'], 2)
            item['number'] = number
            yield item
            del item['product']

    def __len__(self):
        return len(self.cart)

    def get_total_cost(self):
        return sum(round(item['price_ruble'] * item['quantity'], 2) for item in self.cart.values())

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_cart_list(self):
        list_res_ = []
        for element in self:
            list_res_.append(self.get_tr_cart(element['guid']))
        if self.price_exchange:
            self.save()
        return list_res_

    def get_tr_cart(self, product_guid):
        if product_guid not in self.cart:
            return
        item = self.cart[product_guid]

        if 'guid' not in item.keys():
            try:
                product = Product.objects.get(guid=product_guid)
            except Product.DoesNotExist:
                return

            item['code'] = product.code
            item['name'] = product.name
            item['guid'] = product.guid

        item['total_price'] = round(item['price'] * item['quantity'], 2)
        item['total_price_ruble'] = round(item['price_ruble'] * item['quantity'], 2)

        return {'number': item['number'],
                'guid': item['guid'],
                'code': item['code'],
                'name': item['name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'currency': item['currency_name'],
                'total_price': item['total_price'],
                'total_price_ruble': item['total_price_ruble'],
                }

    def view_courses(self):
        currencies_id = [elem['currency_id'] for elem in self.cart.values()]
        currencies = Currency.objects.filter(id__in=currencies_id)
        view = ''
        for currency in currencies:
            course = currency.get_today_course()['course']
            if course != 1:
                view += ' ;' if len(view) > 0 else '' + currency.name.upper() + ': ' + "{0:.4f}".format(course)
        return view

    def get_quantity_product(self, product_guid):
        if product_guid not in self.cart:
            return 0
        return self.cart[product_guid]['quantity']

