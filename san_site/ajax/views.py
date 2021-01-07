import datetime

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.log import log_response

from san_site.cart.cart import Cart
from san_site.models import Section, Product, Order
from san_site.forms import EnterQuantity, EnterQuantityError
from san_site.decorates.decorate import page_not_access_ajax
from san_site.backend.response import HttpResponseAjax, HttpResponseAjaxError
from san_site.backend.tools import str2bool


def get_categories(request):
    try:
        only_stock_ = str2bool(request.GET.get('only_stock'))
    except MultiValueDictKeyError:
        only_stock_ = False
    try:
        obj_section = Section.objects.get(id=Section.get_current_session(request=request))
        guid_initially = obj_section.id
    except Section.DoesNotExist:
        guid_initially = ''
    return HttpResponseAjax(
        result=Section.get_data_for_tree(user=request.user, only_stock=only_stock_),
        guid_initially=guid_initially,
        user_name=request.user.username,
        products=render_to_string('goods.html', {})
    )


@page_not_access_ajax
def get_goods(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET guid')
        log_response(
            '%s : no request GET guid', request.path,
            response=response,
            request=request,
        )
        return response

    try:
        only_stock_ = str2bool(request.GET.get('only_stock'))
    except MultiValueDictKeyError:
        only_stock_ = False

    try:
        only_promo_ = str2bool(request.GET.get('only_promo'))
    except MultiValueDictKeyError:
        only_promo_ = False

    try:
        obj_section = Section.objects.get(id=guid)
    except Section.DoesNotExist:
        response = HttpResponseAjaxError(code=302, message='did not find section')
        log_response(
            '%s : did not find section : %s', request.path, str(guid),
            response=response,
            request=request,
        )
        return response

    obj_section.add_current_session(request)

    is_price_rrp = False

    cart = Cart(request)
    goods_list, kwargs = obj_section.get_goods_list_section_with_kwargs(
        user=request.user, only_stock=only_stock_, only_promo=only_promo_, is_price_rrp=is_price_rrp)

    is_price_rrp = kwargs.get('is_price_rrp', True)

    return HttpResponseAjax(
        current_section=obj_section.full_name,
        products=render_to_string('goods.html', {
            'cart': cart,
            'is_price_rrp': is_price_rrp,
            'goods_list': goods_list,
            'user': request.user
        })
    )


@page_not_access_ajax
def selection(request):
    try:
        only_stock_ = str2bool(request.GET.get('only_stock'))
    except MultiValueDictKeyError:
        only_stock_ = False

    try:
        only_promo_ = str2bool(request.GET.get('only_promo'))
    except MultiValueDictKeyError:
        only_promo_ = False

    try:
        search = request.GET.get('search')
    except MultiValueDictKeyError:
        search = ''

    section_dict = {}
    if search != '' or only_promo_:
        goods_list = Section.get_goods_list(
            user=request.user, search=search, only_stock=only_stock_, only_promo=only_promo_)
    else:
        try:
            obj_section = Section.objects.get(id=Section.get_current_session(request=request))
        except Section.DoesNotExist:
            obj_section = None
        if obj_section is not None:
            section_dict = {'name': obj_section.full_name, 'guid': obj_section.id}
            goods_list = obj_section.get_goods_list_section(
                user=request.user, only_stock=only_stock_, only_promo=only_promo_)
        else:
            goods_list = []

    return HttpResponseAjax(
        section=section_dict,
        products=render_to_string('goods/goods_table.html', {
            'goods_list': goods_list,
            'user': request.user,
        })
    )


@page_not_access_ajax
def cart_add(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET guid')
        log_response(
            '%s : no request GET guid', request.path,
            response=response,
            request=request,
        )
        return response

    try:
        quantity = request.GET.get('quantity')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET quantity')
        log_response(
            '%s : no request GET quantity', request.path,
            response=response,
            request=request,
        )
        return response

    try:
        quantity = int(quantity)
    except TypeError:
        response = HttpResponseAjaxError(code=302, message='no quantity int')
        log_response(
            '%s : no quantity int : %s', request.path, str(quantity),
            response=response,
            request=request,
        )
        return response

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)

    inventory = max(product.get_inventory(cart), 0)
    inventory = 999999 if inventory > 10 else inventory
    quantity = min(quantity, inventory)

    if quantity > 0:
        cart.add(product=product, quantity=quantity)

    return HttpResponseAjax(
        cart=render_to_string('cart/cart.html', {'cart': cart}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart, 'user': request.user})
    )


@page_not_access_ajax
def get_form_images(request):
    if request.method == 'POST':
        pass
    else:
        try:
            guid = request.GET.get('guid')
        except MultiValueDictKeyError:
            response = HttpResponseAjaxError(code=302, message='no request GET guid')
            log_response(
                '%s : no request GET guid', request.path,
                response=response,
                request=request,
            )
            return response

        try:
            product = Product.objects.get(guid=guid)
        except Product.DoesNotExist:
            response = HttpResponseAjaxError(code=303, message='did not find product')
            log_response(
                '%s : did not find product : %s', request.path, str(guid),
                response=response,
                request=request,
            )
            return response

        try:
            height = int(request.GET.get('height'))
        except TypeError:
            height = 699

        if height > 700:
            max_width = 1055
            max_height = 745
        else:
            max_width = 531
            max_height = 521

        return HttpResponseAjax(
            guid=guid,
            height=max_height,
            width=max_width,
            form_images=render_to_string('goods/show_images.html',
                                         {'guid': guid, 'image': ('media/' + str(product.image)),
                                          'max_width': max_width, 'max_height': max_height, 'name': str(product.name)})
        )


@page_not_access_ajax
def cart_get_form_quantity(request):
    if request.method == 'POST':
        pass
    else:
        try:
            guid = request.GET.get('guid')
        except MultiValueDictKeyError:
            response = HttpResponseAjaxError(code=302, message='no request GET guid')
            log_response(
                '%s : no request GET guid', request.path,
                response=response,
                request=request,
            )
            return response

        try:
            product = Product.objects.get(guid=guid)
        except Product.DoesNotExist:
            response = HttpResponseAjaxError(code=302, message='did not find product')
            log_response(
                '%s : did not find product : %s', request.path, str(guid),
                response=response,
                request=request,
            )
            return response

        cart = Cart(request)
        is_cart = (cart.get_quantity_product(product.guid) > 0)

        inventory = max(product.get_inventory(cart), 0)
        inventory = 999999 if inventory > 10 else inventory
        if not is_cart and inventory > 0:
            form = EnterQuantity(initial={'quantity': 1}, max_value=inventory)
        else:
            form = EnterQuantityError()

        return HttpResponseAjax(
            guid=guid,
            inventory=inventory,
            form_enter_quantity=render_to_string('goods/enter_quantity.html',
                                                 {'form': form, 'guid': guid, 'inventory': inventory,
                                                  'is_cart': is_cart})
        )


@page_not_access_ajax
def cart_add_quantity(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET guid')
        log_response(
            '%s : no request GET guid', request.path,
            response=response,
            request=request,
        )
        return response

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)

    quantity = 1
    inventory = max(product.get_inventory(cart), 0)
    inventory = 999999 if inventory > 10 else inventory
    quantity = min(quantity, inventory)

    cart.add(product=product, quantity=quantity)

    elem_cart = cart.get_tr_cart(guid)

    return HttpResponseAjax(
        td_cart_quantity=render_to_string('cart/td_cart_quantity.html', {'goods': elem_cart}),
        td_cart_total_price=render_to_string('cart/td_cart_total_price.html', {'goods': elem_cart}),
        td_cart_total_price_ruble=render_to_string('cart/td_cart_total_price_ruble.html', {'goods': elem_cart}),
        header_cart=render_to_string('cart/header_cart.html', {'cart': cart, 'user': request.user}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart, 'user': request.user})
    )


@page_not_access_ajax
def cart_reduce_quantity(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET guid')
        log_response(
            '%s : no request GET guid', request.path,
            response=response,
            request=request,
        )
        return response

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
        header_cart=render_to_string('cart/header_cart.html', {'cart': cart, 'user': request.user}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart, 'user': request.user})
    )


@page_not_access_ajax
def cart_delete_row(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET guid')
        log_response(
            '%s : no request GET guid', request.path,
            response=response,
            request=request,
        )
        return response

    cart = Cart(request)
    product = get_object_or_404(Product, guid=guid)
    cart.remove(product)

    return HttpResponseAjax(
        header_cart=render_to_string('cart/header_cart.html', {'cart': cart, 'user': request.user}),
        user_cart=render_to_string('header/user_tools_cart.html', {'cart': cart, 'user': request.user})
    )


@page_not_access_ajax
def get_help_tip(request):
    try:
        guid = request.GET.get('guid')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET guid')
        log_response(
            '%s : no request GET guid', request.path,
            response=response,
            request=request,
        )
        return response

    product = get_object_or_404(Product, guid=guid)

    return HttpResponseAjax(
        help_tip=render_to_string('goods/help_tip.html', {'ob_goods': product})
    )


@page_not_access_ajax
def get_orders_list(request):
    try:
        begin_date = request.GET.get('begin_date')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET begin_date')
        log_response(
            '%s : no request GET begin_date', request.path,
            response=response,
            request=request,
        )
        return response
    try:
        end_date = request.GET.get('end_date')
    except MultiValueDictKeyError:
        response = HttpResponseAjaxError(code=302, message='no request GET end_date')
        log_response(
            '%s : no request GET end_date', request.path,
            response=response,
            request=request,
        )
        return response

    begin_date = datetime.date(int(begin_date.split('.')[2]),
                               int(begin_date.split('.')[1]),
                               int(begin_date.split('.')[0]))

    end_date = datetime.date(int(end_date.split('.')[2]),
                             int(end_date.split('.')[1]),
                             int(end_date.split('.')[0]))

    Order.add_current_session(request, begin_date, end_date)

    orders_list = Order.get_orders_list(request.user, begin_date, end_date)
    return HttpResponseAjax(
        list_orders=render_to_string('orders/list_orders_table.html', {
            'orders_list': orders_list
        })
    )
