import json

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError

from san_site.cart.cart import Cart
from san_site.models import Section, Product


def get_categories(request):

    sections = Section.objects.filter(is_deleted=False).order_by('sort', 'name')
    data = []

    for obj in sections:
        parent = '#' if obj.parent_guid == '---' else obj.parent_guid
        data.append({'id': obj.guid, 'parent': parent, 'text': obj.name, 'href': obj.guid})
    str_json = json.dumps(
        {
            'code': 'success',
            'result': data,
            'user_name': request.user.username,
            'goods_html': render_to_string('goods.html', {})
        }
    )
    return HttpResponse(str_json, content_type="application/json", status=200)


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

    return JsonResponse(
        {
            "result": True,
            'goods_html': render_to_string('goods.html', {
                'cart': cart,
                'goods_list': goods_list,
                'user': request.user,
            }),
        }
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
        section_dict = {'name': obj_section.name, 'guid': obj_section.guid}
        goods_list = obj_section.get_goods_list_section(
            user=request.user, only_stock=only_stock_, only_promo=only_promo_)

    return JsonResponse(
        {
            "result": True,
            'section': section_dict,
            'goods_html': render_to_string('goods\goods_table.html', {
                'goods_list': goods_list,
                'user': request.user,
            }),
        })


def cart_add(request):

    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product, quantity=1)

    return JsonResponse(
        {
            "result": True,
            'cart_http': render_to_string('cart/cart.html', {'cart': cart}),
        }
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

    return JsonResponse(
        {
            "result": True,
            'http_quantity': render_to_string('cart/td_cart_quantity.html', {'goods': elem_cart}),
            'http_total_price': render_to_string('cart/td_cart_total_price.html', {'goods': elem_cart}),
            'http_total_price_ruble': render_to_string('cart/td_cart_total_price_ruble.html', {'goods': elem_cart}),
            'header_cart': render_to_string('cart/header_cart.html', {'cart': cart}),
        }
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
    delete_ = elem_cart['quantity'] <= 0

    if delete_:
        cart.remove(product)

    return JsonResponse(
        {
            "result": True,
            'delete': delete_,
            'http_quantity': render_to_string('cart/td_cart_quantity.html', {'goods': elem_cart}),
            'http_total_price': render_to_string('cart/td_cart_total_price.html', {'goods': elem_cart}),
            'http_total_price_ruble': render_to_string('cart/td_cart_total_price_ruble.html', {'goods': elem_cart}),
            'header_cart': render_to_string('cart/header_cart.html', {'cart': cart}),
        }
    )
