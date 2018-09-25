from functools import wraps

from django.conf import settings
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.utils.log import log_response
from django.template.loader import render_to_string
from django.shortcuts import render

from san_site.backend.response import HttpResponseAjax
from san_site.forms import LoginForm


def page_not_access(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user.is_anonymous or not request.user.is_authenticated:
            request.get_full_path()
            resolved_login_url = resolve_url(settings.LOGIN_URL)
            response = HttpResponseRedirect(resolved_login_url)
            log_response(
                'Page Not Allowed (%s): %s', request.user, request.path,
                response=response,
                request=request,
            )
            return response
        return func(request, *args, **kwargs)

    return inner


def page_not_access_ajax(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user.is_anonymous or not request.user.is_authenticated:
            response = HttpResponseAjax(
                current_section='',
                products=render(request, 'account/login_div.html', {'form': LoginForm()}).content.decode()
            )
            log_response(
                'Page Not Allowed (%s): %s', request.user, request.path,
                response=response,
                request=request,
            )
            return response
        return func(request, *args, **kwargs)

    return inner
