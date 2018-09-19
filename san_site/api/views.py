import datetime
import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from san_site.tasks import change_relevant_products as task_change_relevant_products
from san_site.models import \
    Order, Customer, Person, Section, Product, Store, Price, Currency, Inventories, Prices, CustomersPrices, Courses, \
    PricesSale


@csrf_exempt
def api_main(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

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
        dict_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

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
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

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
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

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
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

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
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    update_users(list_load)

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
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    update_users_prices(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
    return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)


@csrf_exempt
def api_courses(request):
    value_response = {'success': True, 'date': [], 'time': {'begin': timezone.now().ctime(), 'end': None}, 'errors': []}

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
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

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
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    if json_str is None:
        add_error(value_response, code='json.ValueError',
                  message='json is empty', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    try:
        list_load = json.loads(json_str)
    except ValueError:
        add_error(value_response, code='json.ValueError',
                  message='error json loads', description='')
        return HttpResponse(json.dumps(value_response), content_type="application/json", status=200)

    update_statuses(list_load, value_response)

    value_response['time']['end'] = timezone.now().ctime()
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
            filter_object[element_list['guid']] = new_object
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

        matrix = 'Основной' if element_list['matrix'] == '' else element_list['matrix']
        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.sort == int(element_list['sort']) \
                    and new_object.matrix == matrix \
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
                                                matrix=matrix,
                                                section=section_obj,
                                                is_deleted=element_list['is_deleted'],
                                                )
            new_object.created_date = timezone.now()
            new_object.save()
            filter_object[element_list['guid']] = new_object
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
        new_object.matrix = matrix
        new_object.is_deleted = element_list['is_deleted']
        new_object.save()

    task_change_relevant_products.delay()


def update_store(load_list):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Store.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object = filter_object.get(element_list['guid'], None)
        if new_object:
            if new_object.name == element_list['name'] \
                    and new_object.code == element_list['code'] \
                    and new_object.sort == int(element_list['sort']) \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.code = element_list['code']
                new_object.sort = int(element_list['sort'])
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
            filter_object[element_list['guid']] = new_object
        else:
            new_object = Store.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              code=element_list['code'],
                                              sort=int(element_list['sort']),
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
                    and new_object.sort == int(element_list['sort']) \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.code = element_list['code']
                new_object.sort = int(element_list['sort'])
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
            filter_object[element_list['guid']] = new_object
        else:
            new_object = Price.objects.create(guid=element_list['guid'],
                                              name=element_list['name'],
                                              code=element_list['code'],
                                              sort=int(element_list['sort']),
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
                    and new_object.sort == int(element_list['sort']) \
                    and new_object.is_deleted == element_list['is_deleted']:
                pass
            else:
                new_object.name = element_list['name']
                new_object.code = element_list['code']
                new_object.sort = int(element_list['sort'])
                new_object.is_deleted = element_list['is_deleted']
                new_object.save()
        else:
            new_object = Currency.objects.create(guid=element_list['guid'],
                                                 name=element_list['name'],
                                                 code=element_list['code'],
                                                 sort=int(element_list['sort']),
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


def update_users(load_list):
    filter_username = [element_list['username'] for element_list in load_list]
    filter_object = {t.username: t for t in User.objects.filter(username__in=filter_username)}

    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object_person = {t.guid: t for t in Person.objects.filter(guid__in=filter_guid)}

    filter_guid = [element_list['guidCustomer'] for element_list in load_list]
    filter_object_customer = {t.guid: t for t in Customer.objects.filter(guid__in=filter_guid)}

    for element_list in load_list:

        new_object_customer = filter_object_customer.get(element_list['guidCustomer'], None)
        if new_object_customer:
            if new_object_customer.name == element_list['nameCustomer'] \
                    and new_object_customer.code == element_list['codeCustomer'] \
                    and new_object_customer.sort == int(element_list['sortCustomer']) \
                    and new_object_customer.is_deleted == element_list['is_deletedCustomer']:
                pass
            else:
                new_object_customer.name = element_list['nameCustomer']
                new_object_customer.code = element_list['codeCustomer']
                new_object_customer.sort = int(element_list['sortCustomer'])
                new_object_customer.is_deleted = element_list['is_deletedCustomer']
                new_object_customer.save()
        else:
            new_object_customer = Customer.objects.create(guid=element_list['guidCustomer'],
                                                          name=element_list['nameCustomer'],
                                                          code=element_list['codeCustomer'],
                                                          sort=int(element_list['sortCustomer']),
                                                          is_deleted=element_list['is_deletedCustomer'],
                                                          )
            new_object_customer.created_date = timezone.now()
            new_object_customer.save()
            filter_object_customer[element_list['guidCustomer']] = new_object_customer

        new_object = filter_object.get(element_list['username'], None)
        if new_object:
            if new_object.first_name == element_list['first_name'] \
                    and new_object.last_name == element_list['last_name'] \
                    and new_object.email == element_list['email'] \
                    and new_object.is_active == element_list['is_active']:
                person = new_object.person
                if person and not person.change_password:
                    new_object.set_password(element_list['password'])
            else:
                new_object.first_name = element_list['first_name']
                new_object.last_name = element_list['last_name']
                new_object.email = element_list['email']
                new_object.is_active = element_list['is_active']
                person = new_object.person
                if person and not person.change_password:
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
            if new_object_person.name == element_list['nameCustomer'] \
                    and new_object_person.code == element_list['codeCustomer'] \
                    and new_object_person.sort == int(element_list['sortCustomer']) \
                    and new_object_person.is_deleted == element_list['is_deletedCustomer']:
                pass
            else:
                new_object_person.name = element_list['name']
                new_object_person.code = element_list['code']
                new_object_person.sort = int(element_list['sort'])
                new_object_person.is_deleted = element_list['is_deleted']
                new_object_person.save()
        else:
            new_object_person = Person.objects.create(guid=element_list['guid'],
                                                      name=element_list['name'],
                                                      user=new_object,
                                                      customer=new_object_customer,
                                                      code=element_list['code'],
                                                      sort=int(element_list['sort']),
                                                      is_deleted=element_list['is_deleted'],
                                                      )
            new_object_person.created_date = timezone.now()
            new_object_person.save()
            filter_object_person[element_list['guid']] = new_object_person


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
    PricesSale.objects.all().delete()

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
                continue

            try:
                value_price = float(element_list_price['value'])
            except ValueError:
                value_price = 0

            new_object = Prices.objects.create(product=obj_product,
                                               price=obj_price,
                                               currency=obj_currency,
                                               value=value_price,
                                               promo=element_list_price['promo'])
            new_object.save()

        load_list_sale = element_list['sale']
        for element_list_sale in load_list_sale:

            if 'currencyGuid' not in element_list_sale.keys():
                continue

            obj_currency = filter_object_currency.get(element_list_sale['currencyGuid'], None)
            if not obj_currency:
                continue

            try:
                value_price = float(element_list_sale['value'])
            except ValueError:
                value_price = 0

            if value_price == 0:
                continue

            new_object = PricesSale.objects.create(product=obj_product,
                                                   currency=obj_currency,
                                                   value=value_price)
            new_object.save()


def update_users_prices(load_list, value_response):
    filter_guid = [element_list['guid'] for element_list in load_list]
    filter_object = {t.guid: t for t in Customer.objects.filter(guid__in=filter_guid)}

    filter_object_currency = {t.guid: t for t in Currency.objects.all()}

    for element_list in load_list:

        obj_customer = filter_object.get(element_list['guid'], None)
        if not obj_customer:
            add_error(value_response, code='Customer.DoesNotExist',
                      message='no get customer', description=element_list)
            continue

        load_list_prices = element_list['price']

        filter_guid = [element_list['productGuid'] for element_list in load_list_prices]
        filter_object_product = {t.guid: t for t in Product.objects.filter(guid__in=filter_guid)}

        CustomersPrices.objects.filter(customer=obj_customer) \
            .filter(product__in=[t for guid, t in filter_object_product.items()]).delete()

        for element_list_price in load_list_prices:

            obj_product = filter_object_product.get(element_list_price['productGuid'], None)
            if not obj_product:
                add_error(value_response, code='Product.DoesNotExist',
                          message='no get product', description=element_list)
                continue

            obj_currency = filter_object_currency.get(element_list_price['currencyGuid'], None)
            if not obj_currency:
                add_error(value_response, code='Currency.DoesNotExist',
                          message='no get currency', description=element_list)
                continue

            try:
                value_discount = float(element_list_price['discount'])
            except ValueError:
                add_error(value_response, code='Prices.ValueError',
                          message='no float discount', description=element_list)
                continue

            try:
                value_percent = float(element_list_price['percent'])
            except ValueError:
                add_error(value_response, code='Prices.ValueError',
                          message='no float percent', description=element_list)
                continue

            new_object = CustomersPrices.objects.create(customer=obj_customer,
                                                        product=obj_product,
                                                        currency=obj_currency,
                                                        discount=value_discount,
                                                        percent=value_percent)
            new_object.save()


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
