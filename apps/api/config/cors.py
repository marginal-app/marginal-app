from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

# Self-hosted, single-user API: the actual security boundary is the bearer
# token (see highlights/auth.py), not CORS. The extension's origin varies per
# browser/install, so we just allow any origin here rather than trying to
# enumerate `chrome-extension://<id>` / `moz-extension://<id>` values.


class CorsMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method == "OPTIONS":
            response = HttpResponse()
        else:
            response = self.get_response(request)

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PATCH, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response
