from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from identity.models import ApiToken
from identity.request import AuthenticatedRequest, IdentityRequest
from identity.tokens import issue_or_rotate


def _login_kwargs(
    request: IdentityRequest,
    *,
    username: str = "",
    has_error: bool = False,
) -> dict[str, object]:
    return {
        "action_url": reverse("identity_login"),
        "csrf_token": get_token(request),
        "username": username,
        "has_error": has_error,
    }


def _token_kwargs(
    request: AuthenticatedRequest,
    *,
    issued_token: str = "",
) -> dict[str, object]:
    token = ApiToken.objects.filter(user=request.user).first()
    hint = token.hint if token is not None else ""
    return {
        "action_url": reverse("identity_token"),
        "logout_url": reverse("identity_logout"),
        "csrf_token": get_token(request),
        "username": request.user.get_username(),
        "hint": hint,
        "issued_token": issued_token,
    }


@require_http_methods(["GET", "POST"])
def login_view(request: IdentityRequest) -> HttpResponse:
    if request.user.is_authenticated and request.bearer_user is None:
        return redirect("identity_settings")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("identity_settings")
        return render(
            request,
            "identity/login.html",
            {"desk_kwargs": _login_kwargs(request, username=username, has_error=True)},
        )
    return render(
        request,
        "identity/login.html",
        {"desk_kwargs": _login_kwargs(request)},
    )


@login_required
@require_http_methods(["POST"])
def logout_view(request: AuthenticatedRequest) -> HttpResponse:
    logout(request)
    return redirect("identity_login")


@login_required
@require_http_methods(["GET"])
def settings_view(request: AuthenticatedRequest) -> HttpResponse:
    return render(
        request,
        "identity/settings.html",
        {"desk_kwargs": _token_kwargs(request)},
    )


@login_required
@require_http_methods(["POST"])
def issue_token_view(request: AuthenticatedRequest) -> HttpResponse:
    plaintext = issue_or_rotate(request.user)
    return render(
        request,
        "identity/settings.html",
        {"desk_kwargs": _token_kwargs(request, issued_token=plaintext)},
    )
