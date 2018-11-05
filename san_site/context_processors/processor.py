from django.conf import settings
import random
from san_site.cart.cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def user(request):
    return {'user': request.user}


def debug(request):
    return {'debug': settings.DEBUG}


def random_css(request):
    if settings.DEBUG:
        return {'random_css': random.randint(0, 99999999999999999)}
    else:
        return {'random_css': ''}
