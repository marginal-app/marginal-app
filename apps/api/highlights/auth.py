import functools
from collections.abc import Callable

from django.http import JsonResponse

from identity.request import IdentityRequest


def require_api_token(view_func: Callable) -> Callable:
    @functools.wraps(view_func)
    def wrapped(request: IdentityRequest, *args, **kwargs):
        if request.bearer_user is None:
            return JsonResponse({"error": "unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapped
