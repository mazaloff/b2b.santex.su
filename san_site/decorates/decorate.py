from functools import wraps

from django.conf import settings
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.utils.log import log_response


def page_not_access(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user.is_anonymous or not request.user.is_authenticated:
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
