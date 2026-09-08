import functools
from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, JsonResponse


def require_api_token(view_func: Callable) -> Callable:
    @functools.wraps(view_func)
    def wrapped(request: HttpRequest, *args, **kwargs):
        expected = f"Bearer {settings.API_TOKEN}"
        if request.headers.get("Authorization") != expected:
            return JsonResponse({"error": "unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapped
