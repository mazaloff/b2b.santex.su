from san_site.cart.cart import Cart


def cart(request):
    return {'cart': Cart(request)}
