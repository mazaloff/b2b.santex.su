import json
from django.http import HttpResponse


class HttpResponseAjax(HttpResponse):
    def __init__(self, success=True, **kwargs):
        kwargs['success'] = success
        super(HttpResponseAjax, self).__init__(
            content=json.dumps(kwargs),
            content_type='application/json',
            status=200
        )


class HttpResponseAjaxError(HttpResponseAjax):
    def __init__(self, code='ERROR AJAX', message=''):
        super(HttpResponseAjaxError, self).__init__(success=False, code=code, message=message)
