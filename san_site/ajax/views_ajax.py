from django.shortcuts import render, redirect, get_object_or_404
from san_site.models import Section, Product
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from san_site.cart.cart import Cart
import json


def get_categories(request):
    sections = Section.objects.all().order_by('sort', 'name')
    data_for = []
    for obj in sections:
        parent = '#' if obj.parent_guid == '---' else obj.parent_guid
        data_for.append({'id': obj.guid, 'parent': parent, 'text': obj.name, 'href': obj.guid})
    str_json = json.dumps({'code': 'success', 'result': data_for})
    return HttpResponse(str_json, content_type="application/json", status=200)


def get_goods(request):
    try:
        guid = request.GET.get('guid')
    except:
        raise HttpResponseBadRequest

    try:
        obj_Section = Section.objects.get(guid=guid)
    except Section.DoesNotExist:
        raise HttpResponseBadRequest

    template_goods_td = 'goods_table_user.html' if request.user.is_authenticated else 'goods_table.html'
    cart = Cart(request)
    goods_list = obj_Section.get_goods_list(request.user)
    cart_goods_list = cart.get_cart_list()

    goods_table_guids = [elem['guid'] for elem in goods_list]
    cart_table_guids = [elem['guid'] for elem in cart_goods_list]

    return JsonResponse({
        "result": True,
        'goods_table': render_to_string(template_goods_td, {'goods_list': goods_list}),
        'goods_table_guids': goods_table_guids,
        'header_cart': render_to_string('header_cart.html', {'cart': cart}),
        'goods_cart': render_to_string('goods_cart_user.html', {'goods_list': cart_goods_list}),
        'cart_table_guids': cart_table_guids,
    })


def cart_add(request):
    try:
        guid = request.GET.get('guid')
    except:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product, quantity=1)

    cart_goods_list = cart.get_cart_list()
    cart_table_guids = [elem['guid'] for elem in cart_goods_list]

    return JsonResponse({
        "result": True,
        'header_cart': render_to_string('header_cart.html', {'cart': cart}),
        'goods_cart': render_to_string('goods_cart_user.html', {'goods_list': cart_goods_list}),
        'cart_table_guids': cart_table_guids
    })


def cart_add_quantity(request):
    try:
        guid = request.GET.get('guid')
    except:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product, quantity=1)

    cart_goods_list = cart.get_cart_list()
    cart_table_guids = [elem['guid'] for elem in cart_goods_list]
    elem_cart = cart.get_tr_cart(guid)

    return JsonResponse({
        "result": True,
        'td_cart_quantity': render_to_string('td_cart_quantity.html', {'goods': elem_cart}),
        'td_cart_total_price': render_to_string('td_cart_total_price.html', {'goods': elem_cart}),
        'td_cart_total_price_ruble': render_to_string('td_cart_total_price_ruble.html', {'goods': elem_cart}),
        'header_cart': render_to_string('header_cart.html', {'cart': cart}),
        'cart_table_guids': cart_table_guids
    })


def cart_reduce_quantity(request):
    try:
        guid = request.GET.get('guid')
    except:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product, quantity=-1)

    cart_goods_list = cart.get_cart_list()
    cart_table_guids = [elem['guid'] for elem in cart_goods_list]
    elem_cart = cart.get_tr_cart(guid)

    return JsonResponse({
        "result": True,
        'delete': elem_cart['quantity'] <= 0,
        'td_cart_quantity': render_to_string('td_cart_quantity.html', {'goods': elem_cart}),
        'td_cart_total_price': render_to_string('td_cart_total_price.html', {'goods': elem_cart}),
        'td_cart_total_price_ruble': render_to_string('td_cart_total_price_ruble.html', {'goods': elem_cart}),
        'header_cart': render_to_string('header_cart.html', {'cart': cart}),
        'cart_table_guids': cart_table_guids
    })
