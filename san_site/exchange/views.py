import datetime
import json

import base64
import dateutil.parser
import os
import tempfile
from django.contrib.auth.models import User
from django.core.files import File
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt

from san_site.models import \
    Order, Customer, Person, Section, Brand, Product, Store, Price, Currency, Inventories, Prices, \
    CustomersPrices, CustomersPrices2020, CustomersPrices2021, CustomersPrices2022, CustomersPrices2023, \
    CustomersPrices2024, CustomersPrices2025, CustomersPrices2026, CustomersPrices2027, \
    Courses, PersonRestrictions, PersonStores, Bill


@csrf_exempt
def api_main(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        dict_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if 'sections' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not sections', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if 'brands' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not brands', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if 'products' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not products', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if 'stores' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not stores', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if 'priceTypes' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not priceTypes', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if 'currencys' not in dict_load is None:
        add_error(value_response, code='json.ValueError',
                  message='json is not currencys', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    update_section(dict_load['sections'])
    update_brand(dict_load['brands'])
    update_product(dict_load['products'])
    update_store(dict_load['stores'])
    update_price(dict_load['priceTypes'])
    update_currency(dict_load['currencys'])

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_photo_of_good(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    key = request.META['HTTP_ID']
    extension = request.META['HTTP_EXTENSION']
    try:
        product_obj = Product.objects.get(guid=key)
    except Product.DoesNotExist:
        add_error(value_response, code='Product.DoesNotExist',
                  message='does not exist', description=key)
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if product_obj.image.name != '':
        try:
            if os.path.exists(product_obj.image.path):
                os.remove(product_obj.image.path)
        except OSError:
            add_error(value_response, code='os.OSError',
                      message='not can remove file', description=f'{product_obj.code} {product_obj.name}')

    body = request.body
    with tempfile.TemporaryFile() as fp:
        fp.write(body)
        product_obj.image.save(key + "." + extension, File(fp), save=True)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def bill_of_order(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    body = request.body
    json_str = body[body.find(b'$%$%$') + 5:len(body)].decode('utf-8')
    body = base64.b64decode(body[0: body.find(b'$%$%$')])

    try:
        data_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    guid = data_load['guid']
    guid_order = data_load['guid_order']
    extension = data_load['extension']
    date = data_load['date']
    number = data_load['number']
    comment = data_load['comment']
    total = data_load['total']
    currency = data_load['currency']

    try:
        order_obj = Order.objects.get(guid=guid_order)
    except Order.DoesNotExist:
        add_error(value_response, code='Order.DoesNotExist',
                  message='does not exist Order', description=guid_order)
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        currency_obj = Currency.objects.get(guid=currency)
    except Currency.DoesNotExist:
        add_error(value_response, code='Currency.DoesNotExist',
                  message='does not exist Currency', description=currency)
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        bill_obj = Bill.objects.get(guid=guid)
    except Bill.DoesNotExist:
        bill_obj = None

    if bill_obj and bill_obj.file.name != '':
        try:
            if os.path.exists(bill_obj.file.path):
                os.remove(bill_obj.file.path)
        except OSError:
            add_error(value_response, code='os.OSError',
                      message='not can remove file', description=f'{bill_obj.number} {bill_obj.date}')

    date = dateutil.parser.parse(date)

    if not bill_obj:
        bill_obj = Bill.objects.create(guid=guid,
                                       order=order_obj,
                                       date=make_aware(date),
                                       number=number,
                                       person=order_obj.person,
                                       customer=order_obj.customer,
                                       total=total,
                                       currency=currency_obj,
                                       comment=comment)
    bill_obj.date = make_aware(date)
    bill_obj.number = number
    bill_obj.total = total
    bill_obj.currency = currency_obj
    bill_obj.comment = comment
    bill_obj.save()

    with tempfile.TemporaryFile() as fp:
        fp.write(body)
        bill_obj.file.save(guid + "." + extension, File(fp), save=True)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_inventories(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    update_inventories(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_prices(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    update_prices(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_users(request):
    value_response = {'success': True, 'date': [], 'result': [],
                      'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    update_users(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_users_prices(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    update_users_prices(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json",
                        status=200 if value_response['success'] else 210)


@csrf_exempt
def api_courses(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    update_courses(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_statuses(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

    try:
        json_str = request.body.decode()
    except UnicodeError:
        add_error(value_response, code='decode.UnicodeError',
                  message='error body decode', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=401)

    update_statuses(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


def update_brand(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Brand.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.code = element_list['code']
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
            filter_object[element_list['guid']] = new_object
        else:
            new_object = Brand.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              code=element_list['code'],
                                              is_deleted=element_list['is_deleted'],
                                              )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object


def update_section(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Section.objects.filter(guid__in=filter_guid)}

    filter_group_guid = [element_list['parentGuid'] for element_list in load_list if element_list['parentGuid'] != '']
    filter_group_object = {t.guid: t for t in Section.objects.filter(guid__in=filter_group_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.is_deleted == element_list['is_deleted']:
                continue
        else:
            new_object = Section.objects.create(guid=element_list['guid'],
                                                name=element_list['name'],
                                                code=element_list['code'],
                                                is_deleted=element_list['is_deleted'],
                                                )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object
            continue

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()

    for element_list in load_list:
        new_object = filter_object.get(element_list['guid'], None)
        if new_object is None:
            continue
        if element_list['parentGuid'] == '':
            if new_object.group is not None:
                new_object.group = None
                new_object.save()
            continue
        parent_object = filter_group_object.get(element_list['parentGuid'], None)
        if parent_object is None:
            continue
        if new_object.group == parent_object:
            continue
        new_object.group = parent_object
        new_object.save()


def update_product(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Product.objects.filter(
        guid__in=filter_guid).select_related('section').select_related('brand')}

    i = 0
    for element_list in load_list:
        i += 1

        matrix = 'Основной' if element_list['matrix'] == '' else element_list['matrix']
        new_object = filter_object.get(element_list['guid'], None)

        guid_section = '' if new_object is None or new_object.section is None else new_object.section.guid
        guid_brand = '' if new_object is None or new_object.brand is None else new_object.brand.guid

        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.code_brand == element_list['code_brand'] \
                    and new_object.matrix == matrix \
                    and new_object.barcode == element_list['barcode'] \
                    and guid_section == element_list['sectionGuid'] \
                    and guid_brand == element_list['brandGuid'] \
                    and new_object.is_deleted == element_list['is_deleted'] \
                    and (not new_object.is_image or (new_object.is_image == element_list['is_image'])):
                continue
            if element_list['is_deleted']:
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
                new_object.clear_inventories()
        else:
            if element_list['is_deleted']:
                continue
            try:
                section_obj = Section.objects.get(guid=element_list['sectionGuid'])
            except Section.DoesNotExist:
                continue
            try:
                brand_obj = Brand.objects.get(guid=element_list['brandGuid'])
            except Brand.DoesNotExist:
                brand_obj = None
            new_object = Product.objects.create(guid=element_list['guid'],
                                                name=element_list['name'],
                                                code=element_list['code'],
                                                code_brand=element_list['code_brand'],
                                                matrix=matrix,
                                                barcode=element_list['barcode'],
                                                section=section_obj,
                                                brand=brand_obj,
                                                is_deleted=element_list['is_deleted'],
                                                )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object
            continue

        if guid_section != element_list['sectionGuid']:
            try:
                section_obj = Section.objects.get(guid=element_list['sectionGuid'])
            except Section.DoesNotExist:
                continue
            new_object.section = section_obj

        if guid_brand != element_list['brandGuid']:
            try:
                brand_obj = Brand.objects.get(guid=element_list['brandGuid'])
            except Brand.DoesNotExist:
                continue
            new_object.brand = brand_obj

        if new_object.is_image and new_object.is_image != element_list['is_image']:
            new_object.image.delete(False)

        new_object.name = element_list['name']
        new_object.code = element_list['code']
        new_object.code_brand = element_list['code_brand']
        new_object.barcode = element_list['barcode']
        new_object.matrix = matrix
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()
        if element_list['is_deleted']:
            new_object.clear_inventories()


def update_store(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Store.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.short_name == element_list['short_name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.short_name = element_list['short_name']
                new_object.code = element_list['code']
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
            filter_object[element_list['guid']] = new_object
        else:
            new_object = Store.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              short_name=element_list['short_name'],
                                              code=element_list['code'],
                                              is_deleted=element_list['is_deleted'],
                                              )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object


def update_price(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Price.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.code = element_list['code']
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
            filter_object[element_list['guid']] = new_object
        else:
            new_object = Price.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              code=element_list['code'],
                                              is_deleted=element_list['is_deleted'],
                                              )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object


def update_currency(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Currency.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.code = element_list['code']
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
        else:
            new_object = Currency.objects.create(guid=element_list['guid'],
                                                 name=element_list['name'],
                                                 code=element_list['code'],
                                                 is_deleted=element_list['is_deleted'],
                                                 )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object


def update_courses(load_list, value_response):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Currency.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        obj_currency = filter_object.get(element_list['guid'], None)
        if not obj_currency:
            add_error(value_response, code='Currency.DoesNotExist',
                      message='no get currency', description=element_list)
            continue

        load_list_courses = element_list['courses']
        filter_date = [datetime.date(
            int(element_list['year']),
            int(element_list['month']),
            int(element_list['day'])) for element_list in load_list_courses]

        Courses.objects.filter(currency=obj_currency).filter(date__in=filter_date).delete()

        for element_list_course in load_list_courses:
            new_object = Courses.objects.create(currency=obj_currency,
                                                date=datetime.date(
                                                    int(element_list_course['year']),
                                                    int(element_list_course['month']),
                                                    int(element_list_course['day'])),
                                                course=element_list_course['course'],
                                                multiplicity=element_list_course['multiplicity'])
            new_object.save()


def update_users(load_list, value_response):
    filter_username = [element_list['username'] for element_list in load_list]
    filter_object = {t.username: t for t in User.objects.filter(username__in=filter_username)}

    filter_object_prices = {t.guid: t for t in Price.objects.all()}
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object_person = {t.guid: t for t in Person.objects.filter(guid__in=filter_guid)}

    filter_guid = []
    for element_list in load_list:
        element_list_customers = element_list['customers']
        for element_list_customer in element_list_customers:
            filter_guid.append(element_list_customer['guid'])
    filter_object_customer = {t.guid: t for t in Customer.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        element_list_customers = element_list['customers']
        for element_list_customer in element_list_customers:
            obj_price = filter_object_prices.get(element_list_customer['guidPrice'], None)
            if not obj_price:
                add_error(value_response, code='Price.DoesNotExist',
                          message='no get price', description=element_list)
                continue
            new_object_customer = filter_object_customer.get(element_list_customer['guid'], None)
            if new_object_customer:
                if new_object_customer.name == element_list_customer['name'] \
                        and new_object_customer.guid_owner == element_list_customer['guidOwner'] \
                        and new_object_customer.code == element_list_customer['code'] \
                        and new_object_customer.is_deleted == element_list_customer['is_deleted']\
                        and new_object_customer.price_id == obj_price.id:
                    pass
                else:
                    new_object_customer.name = element_list_customer['name']
                    new_object_customer.guid_owner = element_list_customer['guidOwner']
                    new_object_customer.code = element_list_customer['code']
                    new_object_customer.is_deleted = element_list_customer['is_deleted']
                    new_object_customer.price = obj_price
                    new_object_customer.save()
            else:
                new_object_customer = Customer.objects.create(guid=element_list_customer['guid'],
                                                              guid_owner=element_list_customer['guidOwner'],
                                                              name=element_list_customer['name'],
                                                              code=element_list_customer['code'],
                                                              is_deleted=element_list_customer['is_deleted'],
                                                              price=obj_price
                                                              )
                new_object_customer.created_date = timezone.now()
                new_object_customer.suffix = str(timezone.now().year)
                new_object_customer.price = obj_price
                new_object_customer.save()
                filter_object_customer[element_list_customer['guid']] = new_object_customer

        new_object = filter_object.get(element_list['username'], None)
        if new_object:
            if new_object.first_name == element_list['first_name'] \
                    and new_object.last_name == element_list['last_name'] \
                    and new_object.email == element_list['email'] \
                    and new_object.is_active == element_list['is_active'] \
                    and not element_list['change_password']:
                pass
            else:
                new_object.first_name = element_list['first_name']
                new_object.last_name = element_list['last_name']
                new_object.email = element_list['email']
                new_object.is_active = element_list['is_active']

                if element_list['change_password']:
                    new_object.set_password(element_list['password'])
                new_object.save()
        else:
            new_object = User.objects.create(username=element_list['username'],
                                             first_name=element_list['first_name'],
                                             last_name=element_list['last_name'],
                                             email=element_list['email'],
                                             is_active=element_list['is_active']
                                             )
            new_object.created_date = timezone.now()
            new_object.set_password(element_list['password'])
            new_object.save()

            filter_object[element_list['username']] = new_object

        new_object_person = filter_object_person.get(element_list['guid'], None)
        if new_object_person:
            if new_object_person.name == element_list['name'] \
                    and new_object_person.code == element_list['code'] \
                    and new_object_person.is_deleted == element_list['is_deleted'] \
                    and new_object_person.allow_order == element_list['allow_order'] \
                    and new_object_person.allow_prices == element_list['allow_prices'] \
                    and new_object_person.permit_all_orders == element_list['permit_all_orders'] \
                    and new_object_person.user == (None if element_list['is_deleted'] else new_object) \
                    and new_object_person.customer == filter_object_customer[element_list['guidOwner']] \
                    and new_object_person.has_restrictions == element_list['has_restrictions']\
                    and new_object_person.has_blok == element_list['has_blok']:
                pass
            else:
                new_object_person.name = element_list['name']
                new_object_person.code = element_list['code']
                new_object_person.allow_order = element_list['allow_order']
                new_object_person.allow_prices = element_list['allow_prices']
                new_object_person.permit_all_orders = element_list['permit_all_orders']
                new_object_person.is_deleted = element_list['is_deleted']
                new_object_person.has_restrictions = element_list['has_restrictions']
                new_object_person.has_blok = element_list['has_blok']
                new_object_person.user = (None if element_list['is_deleted'] else new_object)
                new_object_person.customer = filter_object_customer[element_list['guidOwner']]
                new_object_person.save()
        else:
            qs_persons = Person.objects.filter(user=new_object)
            for each in qs_persons:
                each.user = None
                each.is_deleted = True
                each.save()

            new_object_person = Person.objects.create(guid=element_list['guid'],
                                                      name=element_list['name'],
                                                      user=new_object,
                                                      customer=filter_object_customer[element_list['guidOwner']],
                                                      code=element_list['code'],
                                                      allow_order=element_list['allow_order'],
                                                      allow_prices=element_list['allow_prices'],
                                                      permit_all_orders=element_list['permit_all_orders'],
                                                      is_deleted=element_list['is_deleted'],
                                                      has_restrictions=element_list['has_restrictions'],
                                                      has_blok=element_list['has_blok']
                                                      )
            new_object_person.created_date = timezone.now()
            new_object_person.save()
            filter_object_person[element_list['guid']] = new_object_person

        PersonRestrictions.objects.filter(person=new_object_person).delete()

        if new_object_person.has_restrictions:
            filter_guid_section = [element_list_['guid'] for element_list_ in element_list["restrictions"]]
            filter_object_section = [t for t in Section.objects.filter(guid__in=filter_guid_section)]
            for element_section in filter_object_section:
                PersonRestrictions.objects.create(person=new_object_person, section=element_section)

        PersonStores.objects.filter(person=new_object_person).delete()

        filter_guid_stores = [element_list_['guid'] for element_list_ in element_list["stores"]]
        filter_object_stores = [t for t in Store.objects.filter(guid__in=filter_guid_stores)]
        for element_store in filter_object_stores:
            PersonStores.objects.create(person=new_object_person, store=element_store)

        value_response['result'].append(dict(guid=element_list['guid']))


def update_inventories(load_list, value_response):
    Inventories.objects.all().delete()

    filter_guid = [element_list['productGuid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}
    filter_object_stores = {t.guid: t for t in Store.objects.all()}

    list_obj = []
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

            try:
                reserve = int(element_list_stores['reserve'])
            except ValueError:
                add_error(value_response, code='Inventories.ValueError',
                          message='no int reserve inventories', description=element_list)
                continue

            new_object = Inventories(product=obj_product,
                                     store=obj_store,
                                     quantity=quantity,
                                     reserve=reserve)

            list_obj.append(new_object)

    Inventories.objects.bulk_create(list_obj, batch_size=10000)

    Section.change_is_inventories()
    Section.change_is_deleted()


def update_prices(load_list, value_response):
    Prices.objects.all().delete()

    filter_guid = [element_list['productGuid'] for element_list in load_list]

    filter_object = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}
    filter_object_prices = {t.guid: t for t in Price.objects.all()}
    filter_object_currency = {t.guid: t for t in Currency.objects.all()}

    list_obj_prices = []

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
                continue

            try:
                value_price = float(element_list_price['value'])
            except ValueError:
                value_price = 0

            try:
                value_rrp = float(element_list_price['rrp'])
            except ValueError:
                value_rrp = 0

            new_object = Prices(product=obj_product,
                                price=obj_price,
                                currency=obj_currency,
                                value=value_price,
                                rrp=value_rrp)
            list_obj_prices.append(new_object)

    Prices.objects.bulk_create(list_obj_prices, batch_size=10000)


def update_users_prices(load_list, value_response):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Customer.objects.filter(guid__in=filter_guid)}

    filter_object_currency = {t.guid: t for t in Currency.objects.all()}

    for element_list in load_list:

        list_obj_prices = []
        manager_customers_prices = CustomersPrices

        obj_customer = filter_object.get(element_list['guid'], None)
        all_clean = element_list['allClean']

        if not obj_customer:
            add_error(value_response, code='Customer.DoesNotExist',
                      message='no get customer', description=element_list)
            continue

        if obj_customer.suffix == '2020':
            manager_customers_prices = CustomersPrices2020
        elif obj_customer.suffix == '2021':
            manager_customers_prices = CustomersPrices2021
        elif obj_customer.suffix == '2022':
            manager_customers_prices = CustomersPrices2022
        elif obj_customer.suffix == '2023':
            manager_customers_prices = CustomersPrices2023
        elif obj_customer.suffix == '2024':
            manager_customers_prices = CustomersPrices2024
        elif obj_customer.suffix == '2025':
            manager_customers_prices = CustomersPrices2025
        elif obj_customer.suffix == '2026':
            manager_customers_prices = CustomersPrices2026
        elif obj_customer.suffix == '2027':
            manager_customers_prices = CustomersPrices2027

        load_list_prices = element_list['price']

        filter_guid = [element_list['productGuid'] for element_list in load_list_prices]
        filter_object_product = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}

        if all_clean:
            manager_customers_prices.objects.filter(customer=obj_customer).delete()
        else:
            manager_customers_prices.objects.filter(customer=obj_customer) \
                .filter(product__in=[t for guid, t in filter_object_product.items()]).delete()

        for element_list_price in load_list_prices:

            obj_product = filter_object_product.get(element_list_price['productGuid'], None)
            if not obj_product:
                add_error(value_response, code='Product.DoesNotExist',
                          message='no get product', description=element_list_price)
                continue

            obj_currency = filter_object_currency.get(element_list_price['currencyGuid'], None)
            if not obj_currency:
                add_error(value_response, code='Currency.DoesNotExist',
                          message='no get currency', description=element_list_price)
                continue

            try:
                value_discount = float(element_list_price['discount'])
            except ValueError:
                add_error(value_response, code='Prices.ValueError',
                          message='no float discount', description=element_list_price)
                continue

            try:
                value_percent = float(element_list_price['percent'])
            except ValueError:
                add_error(value_response, code='Prices.ValueError',
                          message='no float percent', description=element_list_price)
                continue

            if value_discount == 0:
                continue
            if value_percent == 0:
                continue
            new_object = manager_customers_prices(customer=obj_customer,
                                                  product=obj_product,
                                                  currency=obj_currency,
                                                  discount=value_discount,
                                                  percent=value_percent,
                                                  promo=element_list_price['promo'])
            list_obj_prices.append(new_object)

        try:
            manager_customers_prices.objects.bulk_create(list_obj_prices, batch_size=10000)
        except IntegrityError as e:
            add_error(value_response, code='CustomersPrices.ValueError', message='error bulk_create',
                      description=str(e))


def update_statuses(load_list, value_response):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Order.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        obj_order = filter_object.get(element_list['guid'], None)
        if not obj_order:
            add_error(value_response, code='Order.DoesNotExist',
                      message='no get order', description=element_list)
            value_response['date'].append(element_list['guid'])
            continue

        obj_order.status = element_list['status']
        obj_order.save()
        value_response['date'].append(element_list['guid'])


def add_error(value_response, **kwargs):
    value_response['success'] = False
    value_response['errors'].append(kwargs)
    value_response['time']['end'] = timezone.now().ctime()
