import json

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError

from san_site.cart.cart import Cart
from san_site.models import Section, Product
from san_site.forms import EnterQuantity


class HttpResponseAjax(HttpResponse):
    def __init__(self, success=True, **kwargs):
        kwargs['success'] = success
        super(HttpResponseAjax, self).__init__(
            content=json.dumps(kwargs),
            content_type='application/json',
            status=200
        )


class HttpResponseAjaxError(HttpResponseAjax):
    def __init__(self, code='ERROR AJAX', message=''):
        super(HttpResponseAjaxError, self).__init__(success=False, code=code, message=message)


def get_categories(request):

    sections = Section.objects.filter(is_deleted=False).order_by('sort', 'name')
    data = []

    for obj in sections:
        parent = '#' if obj.parent_guid == '---' else obj.parent_guid
        data.append({'id': obj.guid, 'parent': parent, 'text': obj.name, 'href': obj.guid})

    return HttpResponseAjax(
        result=data,
        user_name=request.user.username,
        products=render_to_string('goods.html', {})
    )


def get_goods(request):

    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        raise HttpResponseBadRequest

    try:
        only_stock_ = request.GET.get('only_stock')
    except MultiValueDictKeyError:
        only_stock_ = None

    try:
        only_promo_ = request.GET.get('only_promo')
    except MultiValueDictKeyError:
        only_promo_ = None

    try:
        obj_section = Section.objects.get(guid=guid)
    except Section.DoesNotExist:
        raise HttpResponseBadRequest

    obj_section.add_current_session(request)

    cart = Cart(request)
    goods_list = obj_section.get_goods_list_section(
        user=request.user, only_stock=only_stock_, only_promo=only_promo_)

    return HttpResponseAjax(
        current_section=obj_section.full_name,
        products=render_to_string('goods.html', {
            'cart': cart,
            'goods_list': goods_list,
            'user': request.user
        })
    )


def selection(request):
    try:
        only_stock_ = request.GET.get('only_stock')
    except MultiValueDictKeyError:
        only_stock_ = None

    try:
        only_promo_ = request.GET.get('only_promo')
    except MultiValueDictKeyError:
        only_promo_ = None

    try:
        search = request.GET.get('search')
    except MultiValueDictKeyError:
        search = None

    section_dict = {}
    if search != '' or only_promo_ == 'true':
        goods_list = Section.get_goods_list(
            user=request.user, search=search, only_stock=only_stock_, only_promo=only_promo_)
    else:
        try:
            obj_section = Section.objects.get(id=Section.get_current_session(request=request))
        except Section.DoesNotExist:
            return JsonResponse({"result": False})
        section_dict = {'name': obj_section.full_name, 'guid': obj_section.guid}
        goods_list = obj_section.get_goods_list_section(
            user=request.user, only_stock=only_stock_, only_promo=only_promo_)

    return HttpResponseAjax(
        section=section_dict,
        products=render_to_string('goods\goods_table.html', {
            'goods_list': goods_list,
            'user': request.user,
        })
    )


def cart_add(request):

    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        raise HttpResponseBadRequest

    try:
        quantity = request.GET.get('quantity')
    except MultiValueDictKeyError:
        quantity = 1

    try:
        quantity = int(quantity)
    except MultiValueDictKeyError:
        quantity = 1

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    if quantity > 0:
        cart.add(product=product, quantity=quantity)

    return HttpResponseAjax(
        cart=render_to_string('cart/cart.html', {'cart': cart}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart})
    )


def cart_get_form_quantity(request):
    if request.method == 'POST':
        pass
    else:
        try:
            guid = request.GET.get('guid')
        except MultiValueDictKeyError:
            raise HttpResponseBadRequest

        form = EnterQuantity(request.POST or None, initial={'quantity': ''})

        return HttpResponseAjax(
            guid=guid,
            form_enter_quantity=render_to_string('goods/enter_quantity.html', {'form': form, 'guid': guid})
        )


def cart_add_quantity(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product, quantity=1)

    elem_cart = cart.get_tr_cart(guid)

    return HttpResponseAjax(
        td_cart_quantity=render_to_string('cart/td_cart_quantity.html', {'goods': elem_cart}),
        td_cart_total_price=render_to_string('cart/td_cart_total_price.html', {'goods': elem_cart}),
        td_cart_total_price_ruble=render_to_string('cart/td_cart_total_price_ruble.html', {'goods': elem_cart}),
        header_cart=render_to_string('cart/header_cart.html', {'cart': cart}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart})
    )


def cart_reduce_quantity(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product, quantity=-1)

    elem_cart = cart.get_tr_cart(guid)
    delete_row = elem_cart['quantity'] <= 0

    if delete_row:
        cart.remove(product)

    return HttpResponseAjax(
        delete=delete_row,
        td_cart_quantity=render_to_string('cart/td_cart_quantity.html', {'goods': elem_cart}),
        td_cart_total_price=render_to_string('cart/td_cart_total_price.html', {'goods': elem_cart}),
        td_cart_total_price_ruble=render_to_string('cart/td_cart_total_price_ruble.html', {'goods': elem_cart}),
        header_cart=render_to_string('cart/header_cart.html', {'cart': cart}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart})
    )


def cart_delete_row(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.remove(product)

    return HttpResponseAjax(
        header_cart=render_to_string('cart/header_cart.html', {'cart': cart}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart})
    )
