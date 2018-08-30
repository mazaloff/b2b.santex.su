from san_site.models import Section, Product, Currency
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.db import connection
from django.db.models.query import Prefetch
import json


def get_categories(request):
    sections = Section.objects.all().order_by('sort', 'name')
    sections_guid_id = {element_list.guid: element_list.id for element_list in sections}
    data_for = []
    for obj in sections:
        parent = '#' if obj.parent_guid == '---' else sections_guid_id.get(obj.parent_guid)
        data_for.append({'id': sections_guid_id.get(obj.guid), 'parent': parent, 'text': obj.name, 'href': obj.guid})
    str_json = json.dumps({'code': 'success', 'result': data_for})
    return HttpResponse(str_json, content_type="application/json", status=200)


def get_goods(request):
    try:
        guid = request.GET.get('guid')
    except Section.DoesNotExist:
        raise HttpResponseBadRequest
    return JsonResponse({
        "result": True,
        'content': render_to_string('goods.html', {'goods_list': get_goods_list(guid)})
    })


def get_goods_list(guid):

    list_sections = []
    create_list_sections(guid, list_sections)

    products = Product.objects.filter(section__in=list_sections).order_by('code')\
        .prefetch_related('product_inventories', 'product_prices')
    currencis_dict = {elem_.id: elem_.name for elem_ in Currency.objects.all()}
    list_res = []
    for value_product in products:
        quantity_sum = 0
        for product_inventories in value_product.product_inventories.all():
            quantity_sum += product_inventories.quantity
        price_value = 0
        currency_name = ''
        for product_prices in value_product.product_prices.all():
            price_value = product_prices.value
            currency_name = currencis_dict.get(product_prices.currency_id)
        list_res.append({'code': value_product.code,
                         'name': value_product.name,
                         'quantity': quantity_sum,
                         'price': price_value,
                         'currency': currency_name})

    return list_res


def create_list_sections(object, list_sections):
    if type(object) is str:
        try:
            object = Section.objects.get(guid=object)
            list_sections.append(object)
        except Section.DoesNotExist:
            return
    children = Section.objects.filter(parent_guid=object.guid)
    for child in children:
        list_sections.append(child)
        create_list_sections(child, list_sections)
