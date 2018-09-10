from django.http import Http404
from django.shortcuts import render

from san_site.forms import OrderCreateForm
from san_site.models import Order


def order_create(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(request=request)
            if order:
                return render(request, 'orders/order.html', {'order': order, 'created': True})
    else:
        form = OrderCreateForm

    return render(request, 'orders/create.html', {'form': form})


def order(request, **kwargs):
    order_id = kwargs.get('id', 0)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404()

    return render(request, 'orders/order.html', {'order': order})


def order_list(request):
    return render(request, 'orders/list_orders.html', {
        'orders_list': Order.get_orders_list(request.user)
    })
