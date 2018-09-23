from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.utils.log import log_response

from san_site.decorates.decorate import page_not_access
from san_site.forms import OrderCreateForm
from san_site.models import Order, get_customer
from san_site.tasks import order_request as task_order_request


@page_not_access
def order_create(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order_new = form.save(request=request)
            if order:
                return render(request, 'orders/order.html', {'order': order_new, 'created': True})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/create.html', {'form': form})


@page_not_access
def order(request, **kwargs):
    order_id = kwargs.get('id', 0)
    try:
        order_currently = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404()

    customer = get_customer(request.user)
    if customer == order_currently.person.customer:
        return render(request, 'orders/order.html', {'order': order_currently})
    else:
        response = HttpResponseForbidden()
        log_response(
            'Order %s Not Allowed (%s): %s', order_id, request.user, request.path,
            response=response,
            request=request,
        )
        return response


@page_not_access
def order_request(request, **kwargs):
    order_id = kwargs.get('id', 0)
    try:
        order_currently = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404()

    customer = get_customer(request.user)
    if customer == order_currently.person.customer:
        task_order_request.delay(order_id)
        return render(request, 'orders/order.html', {'order': order_currently})
    else:
        response = HttpResponseForbidden()
        log_response(
            'Order %s Not Allowed (%s): %s', order_id, request.user, request.path,
            response=response,
            request=request,
        )
        return response


@page_not_access
def order_list(request):
    return render(request, 'orders/list_orders.html', {
        'orders_list': Order.get_orders_list(request.user)
    })
