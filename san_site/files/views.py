from django.shortcuts import render, Http404, HttpResponse
from san_site.decorates.decorate import page_not_access
from san_site.backend.create_files import create_files
from san_site.models import get_customer, Customer, CustomersFiles
from django.shortcuts import resolve_url
from django.conf import settings

import os


@page_not_access
def for_loading(request):
    user = request.user
    customer = get_customer(user)
    if not customer:
        files = []
    else:
        files = customer.get_files()
    return render(request, 'files/files_for_loading.html', {'files': files})


@page_not_access
def create(request):
    create_files(request.user)
    return for_loading(request)


@page_not_access
def static(request, **kwargs):
    customer_id = kwargs.get('id', 0)
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        raise Http404()
    user = request.user
    if not customer or get_customer(user) != customer:
        raise Http404()
    name_file = kwargs.get('name_file', 0)
    files = CustomersFiles.objects.filter(name=name_file)
    if len(files) > 0:
        url = resolve_url(f'san_site\\static\\files_for_loading\\{customer_id}\\{name_file}')
        file_path = os.path.join(settings.BASE_DIR, url)
        if not os.path.exists(file_path):
            raise Http404()
        content_type = 'application/vnd.ms-excel'
        response = HttpResponse(open(file_path, mode='rb'), content_type=content_type)
        date = files[0].change_date.date().isoformat().replace('-', '_')
        name_file = date + "_" + name_file
        response['Content-Disposition'] = f'attachment; filename={name_file}'
        response['Content-Length'] = os.path.getsize(file_path)
        return response
    else:
        raise Http404()
