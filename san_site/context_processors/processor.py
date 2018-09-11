from django.conf import settings

from san_site.cart.cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def user(request):
    return {'user': request.user}


def debug(request):
    return {'debug': settings.DEBUG}
