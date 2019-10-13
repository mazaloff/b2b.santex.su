import os

from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import resolve_url, render
from django.http import HttpResponse
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from san_site.models import Brand, Product, Person, CustomersFiles, Currency, get_customer
from san_site.decorates.decorate import page_not_access

from .serializers import ProductSerializer


class ProductListView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @staticmethod
    @api_view(('GET',))
    def get(request):

        current_customer = get_customer(request.user)
        current_customer_id = None
        if current_customer:
            current_customer_id = current_customer.id

        if current_customer_id is None:
            return Response({'error': 'Не удалось авторизовать пользователя'},
                            status=HTTP_403_FORBIDDEN)

        param = [current_customer_id]
        filter_article = request.GET.get('filter_article', '')
        filter_barcode = request.GET.get('filter_barcode', '')
        filter_brand = request.GET.get('filter_brand', '')
        filter_quantity = request.GET.get('filter_quantity', '')

        str_filter_article = ' TRUE '
        if filter_article != '':
            param += [list(map(lambda x: x.upper(), filter_article.split(','))), ]
            str_filter_article = 'UPPER(_product.code::text) = ANY(%s)'

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
                        _product.code_brand AS code_brand_,
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
                        LEFT JOIN san_site_prices _prices ON _product.id = _prices.product_id
                            LEFT JOIN san_site_currency _prices_cur ON _prices.currency_id = _prices_cur.id
                        LEFT JOIN san_site_customersprices _customersprices 
                            ON _customersprices.customer_id = %s AND _product.id = _customersprices.product_id  
                                LEFT JOIN san_site_currency _customersprices_cur 
                                    ON _customersprices.currency_id = _customersprices_cur.id
                        LEFT JOIN san_site_inventories _inventories ON _product.id = _inventories.product_id
                        LEFT JOIN san_site_brand _brand ON _product.brand_id = _brand.id
                    WHERE _product.is_deleted = FALSE
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
    currencies = ', '.join([el.name for el in Currency.objects.filter(is_deleted=False).order_by('name')])
    return render(request, 'files_API.html', {'uid': uid, 'files': files, 'brands': brands, 'currencies': currencies})


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
