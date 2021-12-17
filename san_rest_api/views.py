import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import resolve_url, render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.views import APIView

from san_site.decorates.decorate import page_not_access
from san_site.models import Brand, Product, Customer, Person, Order, CustomersFiles, get_customer, get_person
from .serializers import ProductSerializer, ProductSerializerV1, OrderSerializer


class ProductListView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @staticmethod
    @api_view(('GET',))
    def get(request):

        current_customer = get_customer(request.user)
        current_customer_id = None
        current_customer_price_id = 0
        current_customer_suffix = ''
        if current_customer:
            current_customer_id = current_customer.id
            current_customer_price_id = current_customer.price.id
            current_customer_suffix = current_customer.suffix

        if current_customer_id is None:
            return Response({'error': 'Не удалось авторизовать пользователя'},
                            status=HTTP_403_FORBIDDEN)

        current_person = get_person(request.user)
        current_person_id = 0
        if current_person:
            current_person_id = current_person.id

        param = [current_customer_id]

        filter_code = ''

        for key, value in request.GET.items():
            if key.startswith('filter_code'):
                filter_code += f"{'' if filter_code == '' else ','}{value}"

        filter_article = ''

        for key, value in request.GET.items():
            if key.startswith('filter_article'):
                filter_article += f"{'' if filter_article == '' else ','}{value}"

        filter_barcode = ''

        for key, value in request.GET.items():
            if key.startswith('filter_barcode'):
                filter_barcode += f"{'' if filter_barcode == '' else ','}{value}"

        filter_brand = ''

        for key, value in request.GET.items():
            if key.startswith('filter_brand'):
                filter_brand += f"{'' if filter_brand == '' else ','}{value}"

        filter_quantity = request.GET.get('filter_quantity', '')

        str_filter_code = ' TRUE '
        if filter_code != '':
            param += [list(map(lambda x: x.upper(), filter_code.split(','))), ]
            str_filter_code = 'UPPER(_product.code::text) = ANY(%s)'

        str_filter_article = ' TRUE '
        if filter_article != '':
            param += [list(map(lambda x: x.upper(), filter_article.split(','))), ]
            str_filter_article = 'UPPER(_product.code_brand::text) = ANY(%s)'

        str_filter_barcode = ' TRUE '
        if filter_barcode != '':
            param += [list(map(lambda x: x.upper(), filter_barcode.split(','))), ]
            str_filter_barcode = 'UPPER(_product.barcode::text) = ANY(%s)'

        str_filter_brand = ' TRUE '
        if filter_brand != '':
            param += [list(map(lambda x: x.upper(), filter_brand.split(','))), ]
            str_filter_brand = 'UPPER(_brand.name::text) = ANY(%s)'

        str_filter_quantity = ' TRUE '
        if filter_quantity != '' and filter_quantity.upper() == 'YES':
            str_filter_quantity = 'COALESCE(_inventories.quantity, 0) > 0'

        queryset = Product.objects.raw(
            f"""WITH result AS (
                SELECT _product.id AS id,
                        _product.code AS code_,
                        _product.guid AS guid_,
                        _product.code_brand AS article_,
                        _product.barcode AS barcode_,
                        _product.name AS name_,
                        _product.matrix AS matrix_,
                        _product.image AS image,
                        COALESCE(_brand.name, '') AS brand_name_,
                        COALESCE(_customersprices.discount, COALESCE(_prices.value, 0)) AS price,
                        COALESCE(_customersprices_cur.name, COALESCE(_prices_cur.name, '')) AS currency,
                        COALESCE(_prices.rrp, 0) AS price_rrp,
                        SUM(COALESCE(_inventories.quantity, 0)) AS quantity
                    FROM san_site_product _product
                        LEFT JOIN san_site_prices _prices 
                                ON _product.id = _prices.product_id AND _prices.price_id = {current_customer_price_id}
                            LEFT JOIN san_site_currency _prices_cur ON _prices.currency_id = _prices_cur.id
                        LEFT JOIN san_site_customersprices{current_customer_suffix} _customersprices 
                            ON _customersprices.customer_id = %s AND _product.id = _customersprices.product_id  
                                LEFT JOIN san_site_currency _customersprices_cur 
                                    ON _customersprices.currency_id = _customersprices_cur.id
                        LEFT JOIN san_site_personstores _personstores ON _personstores.person_id = {current_person_id}
                            LEFT JOIN san_site_inventories _inventories 
                                ON _product.id = _inventories.product_id
                                    AND _personstores.store_id = _inventories.store_id
                        LEFT JOIN san_site_brand _brand ON _product.brand_id = _brand.id
                    WHERE _product.is_deleted = FALSE
                        AND {str_filter_code}
                        AND {str_filter_article}
                        AND {str_filter_brand}
                        AND {str_filter_barcode}
                        AND {str_filter_quantity}
                    GROUP BY _product.id,
                        _product.code,
                        _product.code_brand,
                        _product.barcode,
                        _product.name,
                        _product.matrix,
                        _product.image,
                        COALESCE(_brand.name, ''),
                        COALESCE(_prices.value, 0),
                        COALESCE(_customersprices.discount, COALESCE(_prices.value, 0)),
                        COALESCE(_customersprices_cur.name, COALESCE(_prices_cur.name, '')),
                        COALESCE(_prices.rrp, 0)
                    )
                SELECT *
                FROM result
                ORDER BY result.code_;""", param)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class ProductListViewV1(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @staticmethod
    @api_view(('GET',))
    def get(request):

        current_customer = get_customer(request.user)
        current_customer_id = None
        current_customer_price_id = 0
        current_customer_suffix = ''
        if current_customer:
            current_customer_id = current_customer.id
            current_customer_price_id = current_customer.price.id
            current_customer_suffix = current_customer.suffix

        if current_customer_id is None:
            return Response({'error': 'Не удалось авторизовать пользователя'},
                            status=HTTP_403_FORBIDDEN)

        current_person = get_person(request.user)
        current_person_id = 0
        if current_person:
            current_person_id = current_person.id

        param = [current_customer_id]

        filter_id = ''
        for key, value in request.GET.items():
            if key.startswith('filter_id'):
                filter_id += f"{'' if filter_id == '' else ','}{value}"

        filter_code = ''
        for key, value in request.GET.items():
            if key.startswith('filter_code'):
                filter_code += f"{'' if filter_code == '' else ','}{value}"

        filter_article = ''
        for key, value in request.GET.items():
            if key.startswith('filter_article'):
                filter_article += f"{'' if filter_article == '' else ','}{value}"

        filter_barcode = ''
        for key, value in request.GET.items():
            if key.startswith('filter_barcode'):
                filter_barcode += f"{'' if filter_barcode == '' else ','}{value}"

        filter_brand = ''
        for key, value in request.GET.items():
            if key.startswith('filter_brand'):
                filter_brand += f"{'' if filter_brand == '' else ','}{value}"

        filter_quantity = request.GET.get('filter_quantity', '')

        str_filter_id = ' TRUE '
        if filter_id != '':
            param += [list(map(lambda x: x.upper(), filter_id.split(','))), ]
            str_filter_id = 'UPPER(_product.guid::text) = ANY(%s)'

        str_filter_code = ' TRUE '
        if filter_code != '':
            param += [list(map(lambda x: x.upper(), filter_code.split(','))), ]
            str_filter_code = 'UPPER(_product.code::text) = ANY(%s)'

        str_filter_article = ' TRUE '
        if filter_article != '':
            param += [list(map(lambda x: x.upper(), filter_article.split(','))), ]
            str_filter_article = 'UPPER(_product.code_brand::text) = ANY(%s)'

        str_filter_barcode = ' TRUE '
        if filter_barcode != '':
            param += [list(map(lambda x: x.upper(), filter_barcode.split(','))), ]
            str_filter_barcode = 'UPPER(_product.barcode::text) = ANY(%s)'

        str_filter_brand = ' TRUE '
        if filter_brand != '':
            param += [list(map(lambda x: x.upper(), filter_brand.split(','))), ]
            str_filter_brand = 'UPPER(_brand.name::text) = ANY(%s)'

        str_filter_quantity = ' TRUE '
        if filter_quantity != '' and filter_quantity.upper() == 'YES':
            str_filter_quantity = 'COALESCE(_inventories.quantity, 0) > 0'

        queryset = Product.objects.raw(
            f"""WITH result AS (
                SELECT _product.id AS id,
                        _product.code AS code_,
                        _product.guid AS guid_,
                        _product.code_brand AS article_,
                        _product.barcode AS barcode_,
                        _product.name AS name_,
                        _product.matrix AS matrix_,
                        _product.image AS image,
                        COALESCE(_brand.name, '') AS brand_name_,
                        COALESCE(_customersprices.discount, COALESCE(_prices.value, 0)) AS price,
                        COALESCE(_customersprices_cur.name, COALESCE(_prices_cur.name, '')) AS currency,
                        COALESCE(_customersprices_cur.id, COALESCE(_prices_cur.id, 0)) AS currency_id,
                        COALESCE(_prices.rrp, 0) AS price_rrp,
                        COALESCE(_prices.value, 0) AS price_base,
                        SUM(COALESCE(_inventories.quantity, 0)) AS quantity
                    FROM san_site_product _product
                        LEFT JOIN san_site_prices _prices 
                                ON _product.id = _prices.product_id AND _prices.price_id = {current_customer_price_id}
                            LEFT JOIN san_site_currency _prices_cur ON _prices.currency_id = _prices_cur.id
                        LEFT JOIN san_site_customersprices{current_customer_suffix} _customersprices 
                            ON _customersprices.customer_id = %s AND _product.id = _customersprices.product_id  
                                LEFT JOIN san_site_currency _customersprices_cur 
                                    ON _customersprices.currency_id = _customersprices_cur.id
                        LEFT JOIN san_site_personstores _personstores ON _personstores.person_id = {current_person_id}
                            LEFT JOIN san_site_inventories _inventories 
                                ON _product.id = _inventories.product_id
                                    AND _personstores.store_id = _inventories.store_id
                        LEFT JOIN san_site_brand _brand ON _product.brand_id = _brand.id
                    WHERE _product.is_deleted = FALSE
                        AND {str_filter_id}
                        AND {str_filter_code}
                        AND {str_filter_article}
                        AND {str_filter_brand}
                        AND {str_filter_barcode}
                        AND {str_filter_quantity}
                    GROUP BY _product.id,
                        _product.code,
                        _product.code_brand,
                        _product.barcode,
                        _product.name,
                        _product.matrix,
                        _product.image,
                        COALESCE(_brand.name, ''),
                        COALESCE(_prices.value, 0),
                        COALESCE(_customersprices.discount, COALESCE(_prices.value, 0)),
                        COALESCE(_customersprices_cur.name, COALESCE(_prices_cur.name, '')),
                        COALESCE(_customersprices_cur.id, COALESCE(_prices_cur.id, 0)),
                        COALESCE(_prices.rrp, 0)
                    )
                SELECT *
                FROM result
                ORDER BY result.code_;""", param)
        serializer = ProductSerializerV1(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class OrderListView(APIView):
    authentication_classes = ()

    @staticmethod
    @api_view(('GET',))
    def get(request):

        objects = Order.objects

        customer_guid = ''
        for key, value in request.GET.items():
            if key.startswith('customer_guid'):
                customer_guid += f"{'' if customer_guid == '' else ','}{value}"
        if customer_guid != '':
            qr = Customer.objects.filter(guid=customer_guid)
            if len(qr) == 0:
                return Response({'error': 'Не определен покупатель (customer_guid)'},
                                status=HTTP_200_OK)
            customer = qr[0]
            objects = objects.filter(customer=customer)

        person_guid = ''
        for key, value in request.GET.items():
            if key.startswith('person_guid'):
                person_guid += f"{'' if person_guid == '' else ','}{value}"
        if person_guid != '':
            qr = Person.objects.filter(guid=person_guid)
            if len(qr) == 0:
                return Response({'error': 'Не определен юзер (person_guid)'},
                                status=HTTP_200_OK)
            person = qr[0]
            objects = objects.filter(person=person)

        data_start_str = ''
        for key, value in request.GET.items():
            if key.startswith('start'):
                data_start_str += f"{'' if data_start_str == '' else ','}{value}"
        if data_start_str != '':
            try:
                data_start = datetime.strptime(data_start_str, "%Y-%m-%d")
                objects = objects.filter(date__gte=data_start)
            except TypeError:
                return Response({'error': 'Не верная дата (start)'},
                                status=HTTP_200_OK)

        data_end_str = ''
        for key, value in request.GET.items():
            if key.startswith('end'):
                data_end_str += f"{'' if data_end_str == '' else ','}{value}"
        if data_end_str != '':
            try:
                data_end = datetime.strptime(data_end_str, "%Y-%m-%d")
                objects = objects.filter(date__lte=data_end)
            except TypeError:
                return Response({'error': 'Не верная дата (end)'},
                                status=HTTP_200_OK)

        serializer = OrderSerializer(objects.all(), many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class CatalogView(APIView):

    @staticmethod
    @api_view(('GET',))
    @permission_classes((AllowAny,))
    def get(request):

        try:
            uid = request.GET.get('uid')
        except MultiValueDictKeyError:
            return Response({'error': 'Не удалось авторизовать пользователя'}, status=HTTP_403_FORBIDDEN)
        try:
            user = Token.objects.get(key=uid).user
        except Token.DoesNotExist:
            return Response({'error': 'Не удалось авторизовать пользователя'}, status=HTTP_403_FORBIDDEN)

        customer = get_customer(user=user)
        if customer is None:
            return Response({'error': 'Не удалось авторизовать пользователя'}, status=HTTP_403_FORBIDDEN)

        try:
            type_file = request.GET.get('type')
        except MultiValueDictKeyError:
            type_file = 'csv'

        name_file = f'goods_b2b_santex.{type_file}'
        files = CustomersFiles.objects.filter(customer=customer, type_file=type_file)
        if len(files) > 0:
            url = resolve_url(f'san_site/static/files_for_loading/{customer.id}/{name_file}')
            file_path = os.path.join(settings.BASE_DIR, url)
            if not os.path.exists(file_path):
                return Response({'error': 'Нет файла'}, status=HTTP_404_NOT_FOUND)
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(open(file_path, mode='rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename={name_file}'
            response['Content-Length'] = os.path.getsize(file_path)
            return response
        else:
            return Response({'error': 'Нет файла'}, status=HTTP_404_NOT_FOUND)


@page_not_access
def our_api(request):

    customer = get_customer(request.user)
    uid, _ = Token.objects.get_or_create(user=request.user)
    if not customer:
        files = []
    else:
        files = customer.get_files()
        for file in files:
            type_file = file['type']
            file['url'] = f'/api/v1/catalog/?uid={uid}&type={type_file}'

    brands = ', '.join([el.name for el in Brand.objects.filter(is_deleted=False).order_by('name')])
    return render(request, 'files_API.html', {'uid': uid, 'files': files, 'brands': brands})


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if username is None or password is None:
        return Response({'error': 'Нет полей username и password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Не удалось авторизовать пользователя'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)
