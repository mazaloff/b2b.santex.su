from san_site.models import Section
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
import json


def get_categories(request):
    sections = Section.objects.all().order_by('sort', 'name')
    data_for = []
    for obj in sections:
        parent = '#' if obj.parent_guid == '---' else obj.parent_guid
        data_for.append({'id': obj.guid, 'parent': parent, 'text': obj.name, 'href': obj.guid})
    str_json = json.dumps({'code': 'success', 'result': data_for})
    return HttpResponse(str_json, content_type="application/json", status=200)


def get_goods(request):
    try:
        guid = request.GET.get('guid')
    except Section.DoesNotExist:
        raise HttpResponseBadRequest

    try:
        obj_Section = Section.objects.get(guid=guid)
    except Section.DoesNotExist:
        raise HttpResponseBadRequest

    return JsonResponse({
        "result": True,
        'content': render_to_string('goods.html', {'goods_list': obj_Section.get_goods_list()})
    })
