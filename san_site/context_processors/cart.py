from san_site.cart.cart import Cart


def cart(request):
    cart = Cart(request)
    return {
            'cart': cart,
            'cart_goods_list': cart.get_cart_list(),
        }
