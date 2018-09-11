from functools import wraps

from django.http import HttpResponseForbidden
from django.utils.log import log_response


def page_not_access(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.user.is_anonymous or not request.user.is_authenticated:
            response = HttpResponseForbidden()
            log_response(
                'Page Not Allowed (%s): %s', request.user, request.path,
                response=response,
                request=request,
            )
            return response
        return func(request, *args, **kwargs)

    return inner
