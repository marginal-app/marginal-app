from collections.abc import Callable

from django.http import HttpResponse

from identity.request import IdentityRequest
from identity.tokens import user_from_bearer


class BearerTokenMiddleware:
    def __init__(self, get_response: Callable[[IdentityRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: IdentityRequest) -> HttpResponse:
        request.bearer_user = None
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            user = user_from_bearer(header.removeprefix("Bearer ").strip())
            if user is not None:
                request.user = user
                request.bearer_user = user
        return self.get_response(request)
