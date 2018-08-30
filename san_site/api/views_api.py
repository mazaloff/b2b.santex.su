from san_site.models import Section, Product, Store, Price, Currency, Inventories, Prices
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import connection
import json


@csrf_exempt
def api_upsert(request):

    value_response = {'success': True, 'result': [], 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    try:
        list_load = json.loads(json_str[8+json_str.find('&params', 0, 500):])
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if len(list_load) < 1:
        add_error(value_response, code='json.ValueError',
                  message='json is not params', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    dict_load = list_load[0]

    if 'sections' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not sections', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if 'products' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not products', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if 'stores' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not stores', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if 'priceTypes' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not priceTypes', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if 'currencys' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not currencys', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


    update_section(dict_load['sections'])
    update_product(dict_load['products'])
    update_store(dict_load['stores'])
    update_price(dict_load['priceTypes'])
    update_currency(dict_load['currencys'])

    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_inventories(request):

    value_response = {'success': True, 'result': [], 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    try:
        list_load = json.loads(json_str[8+json_str.find('&params', 0, 500):])
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if len(list_load) < 1:
        add_error(value_response, code='json.ValueError',
                  message='json is not params', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    dict_load = list_load[0]

    if 'inventories' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not inventories', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    update_inventories(dict_load['inventories'], value_response)

    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_prices(request):

    value_response = {'success': True, 'result': [], 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    try:
        list_load = json.loads(json_str[8+json_str.find('&params', 0, 500):])
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if len(list_load) < 1:
        add_error(value_response, code='json.ValueError',
                  message='json is not params', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    dict_load = list_load[0]

    if 'prices' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not prices', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    update_prices(dict_load['prices'], value_response)

    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


def update_section(load_list):

    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Section.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        parent_guid = '---' if element_list['parentGuid'] == '' else element_list['parentGuid']

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.sort == int(element_list['sort']) \
                    and new_object.parent_guid == parent_guid \
                    and new_object.is_deleted == element_list['is_deleted']:
                continue
        else:
            new_object = Section.objects.create(guid=element_list['guid'],
                                                name=element_list['name'],
                                                code=element_list['code'],
                                                sort=int(element_list['sort']),
                                                parent_guid=parent_guid,
                                                is_deleted=element_list['is_deleted'],
                                                )
            new_object.created_date = timezone.now()
            new_object.save()
            continue

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.sort = int(element_list['sort'])
        new_object.parent_guid = parent_guid
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()


def update_product(load_list):

    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid).select_related('section')}

    i = 0
    for element_list in load_list:
        i += 1

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.sort == int(element_list['sort']) \
                    and new_object.section.guid == element_list['sectionGuid'] \
                    and new_object.is_deleted == element_list['is_deleted']:
                continue
        else:
            try:
                section_obj = Section.objects.get(guid=element_list['sectionGuid'])
            except Section.DoesNotExist:
                continue
            new_object = Product.objects.create(guid=element_list['guid'],
                                                name=element_list['name'],
                                                code=element_list['code'],
                                                sort=int(element_list['sort']),
                                                section=section_obj,
                                                is_deleted=element_list['is_deleted'],
                                                )
            new_object.created_date = timezone.now()
            new_object.save()
            continue

        if new_object.section.guid != element_list['sectionGuid']:
            try:
                section_obj = Section.objects.get(guid=element_list['sectionGuid'])
            except Section.DoesNotExist:
                continue
            new_object.section = section_obj

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.sort = int(element_list['sort'])
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()


def update_store(load_list):

    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Store.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            pass
        else:
            new_object = Store.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              code=element_list['code'],
                                              sort=int(element_list['sort']),
                                              is_deleted=element_list['is_deleted'],
                                              )
            new_object.created_date = timezone.now()

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.sort = int(element_list['sort'])
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()


def update_price(load_list):

    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Price.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            pass
        else:
            new_object = Price.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              code=element_list['code'],
                                              sort=int(element_list['sort']),
                                              is_deleted=element_list['is_deleted'],
                                              )
            new_object.created_date = timezone.now()

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.sort = int(element_list['sort'])
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()


def update_currency(load_list):

    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Currency.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            pass
        else:
            new_object = Currency.objects.create(guid=element_list['guid'],
                                                 name=element_list['name'],
                                                 code=element_list['code'],
                                                 sort=int(element_list['sort']),
                                                 is_deleted=element_list['is_deleted'],
                                                 )
            new_object.created_date = timezone.now()

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.sort = int(element_list['sort'])
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()


def update_inventories(load_list, value_response):

    Inventories.objects.all().delete()

    filter_guid = [element_list['productGuid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}
    filter_object_stores = {t.guid: t for t in Store.objects.all()}

    for element_list in load_list:

        obj_product = filter_object.get(element_list['productGuid'], None)
        if not obj_product:
            add_error(value_response, code='Product.DoesNotExist',
                      message='no get product', description=element_list)
            continue

        load_list_stores = element_list['inventories']
        for element_list_stores in load_list_stores:

            obj_store = filter_object_stores.get(element_list_stores['storeGuid'], None)
            if not obj_store:
                add_error(value_response, code='Store.DoesNotExist',
                        message='no get store', description=element_list)
                continue

            try:
                quantity = int(element_list_stores['quantity'])
            except ValueError:
                add_error(value_response, code='Inventories.ValueError',
                          message='no int quantity inventories', description=element_list)
                continue

            new_object = Inventories.objects.create(product=obj_product,
                                                    store=obj_store,
                                                    quantity=quantity)
            new_object.save()


def update_prices(load_list, value_response):

    Prices.objects.all().delete()

    filter_guid = [element_list['productGuid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}
    filter_object_prices = {t.guid: t for t in Price.objects.all()}
    filter_object_currency = {t.guid: t for t in Currency.objects.all()}

    for element_list in load_list:

        obj_product = filter_object.get(element_list['productGuid'], None)
        if not obj_product:
            add_error(value_response, code='Product.DoesNotExist',
                      message='no get product', description=element_list)
            continue

        load_list_prices = element_list['price']
        for element_list_price in load_list_prices:

            obj_price = filter_object_prices.get(element_list_price['priceTypeGuid'], None)
            if not obj_price:
                add_error(value_response, code='Price.DoesNotExist',
                          message='no get price', description=element_list)
                continue

            obj_currency = filter_object_currency.get(element_list_price['currencyGuid'], None)
            if not obj_currency:
                add_error(value_response, code='Currency.DoesNotExist',
                          message='no get currency', description=element_list)
                continue

            try:
                value_price = float(element_list_price['value'])
            except ValueError:
                add_error(value_response, code='Prices.ValueError',
                          message='no float value price', description=element_list)
                continue

            new_object = Prices.objects.create(product=obj_product,
                                               price=obj_price,
                                               currency=obj_currency,
                                               value=value_price)
            new_object.save()


def add_error(value_respons, **kwargs):
    value_respons['success'] = False
    value_respons['errors'].append(kwargs)
