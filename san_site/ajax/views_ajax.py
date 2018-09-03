from django.shortcuts import render, redirect, get_object_or_404
from san_site.models import Section, Product
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from san_site.forms import CartAddProductForm
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
    return JsonResponse({
        "result": True,
        'content': render_to_string(template_goods_td, {'goods_list': obj_Section.get_goods_list(request.user)})
    })


def cart_add(request):
    try:
        guid = request.GET.get('guid')
    except:
        raise HttpResponseBadRequest

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.add(product=product,
                 quantity=1)
    return JsonResponse({
        "result": True,
    })


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')
