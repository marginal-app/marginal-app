from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from identity.models import User


class IdentityRequest(HttpRequest):
    """A request after BearerTokenMiddleware — the user may still be anonymous."""

    user: User | AnonymousUser  # pyrefly: ignore[bad-override-mutable-attribute]
    bearer_user: User | None


class AuthenticatedRequest(IdentityRequest):
    """A request whose ``user`` is this project's User.

    Session views behind ``login_required``, and API views behind
    ``require_api_token``.
    """

    user: User  # pyrefly: ignore[bad-override-mutable-attribute]
