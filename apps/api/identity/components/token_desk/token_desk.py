from dataclasses import dataclass
from typing import ClassVar, Self
from urllib.parse import urlparse

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

TOKEN_BLURB = (
    "확장의 설정에 이 서버 주소와 토큰을 넣으면 밑줄이 여기로 모입니다. "
    "토큰은 발급 직후 한 번만 보입니다."
)
ISSUED_WARNING = "이 토큰은 지금만 보입니다. 닫으면 다시 볼 수 없고, 필요하면 다시 발급합니다."
EMPTY_COPY = "확장과 연결할 토큰이 없습니다."
CONNECT_HINT = "확장 아이콘 → 설정 → 서버 주소와 토큰 입력 → 저장하고 연결 확인"
DEFAULT_SERVER_URL = "http://127.0.0.1:8000"


def _host_from_url(server_url: str) -> str:
    parsed = urlparse(server_url)
    return parsed.netloc or server_url


class TokenDesk(Component):
    citry = app
    name = "token_desk"
    template_file = "token_desk.citry-html"
    css_file = "token_desk.css"

    @dataclass
    class Kwargs:
        action_url: str = ""
        logout_url: str = ""
        csrf_token: str = ""
        username: str = ""
        hint: str = ""
        issued_token: str = ""
        server_url: str = DEFAULT_SERVER_URL

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(username="dev"),
                    slug="identity-token-empty",
                    title="TokenDesk / empty",
                    description="Settings — sidebar expanded, no token yet.",
                ),
                meta(
                    variant(
                        username="dev",
                        hint="k3x9",
                        issued_token="dev-token-plain-k3x9",
                    ),
                    slug="identity-token-issued",
                    title="TokenDesk / issued",
                    description="Plaintext shown once with a copy pill.",
                ),
                meta(
                    variant(username="dev", hint="k3x9"),
                    slug="identity-token-has",
                    title="TokenDesk / has",
                    description="Masked token and hint — rotate to see a new secret.",
                ),
            ]

    def template_data(self, kwargs, slots):
        has_issued = bool(kwargs.issued_token)
        has_hint_only = bool(kwargs.hint) and not kwargs.issued_token
        has_token = bool(kwargs.hint or kwargs.issued_token)
        host = _host_from_url(kwargs.server_url)
        initials = (kwargs.username[:1] or "M").upper()
        if has_issued:
            token_kicker = "방금 발급"
        elif has_hint_only:
            token_kicker = f"끝자리 {kwargs.hint}"
        else:
            token_kicker = "없음"
        return {
            "action_url": kwargs.action_url,
            "logout_url": kwargs.logout_url,
            "csrf_token": kwargs.csrf_token,
            "username": kwargs.username,
            "hint": kwargs.hint,
            "issued_token": kwargs.issued_token,
            "server_url": kwargs.server_url,
            "has_issued": has_issued,
            "has_hint_only": has_hint_only,
            "show_logout_form": bool(kwargs.logout_url),
            "submit_label": "다시 발급" if has_token else "토큰 발급",
            "initials": initials,
            "account_meta": f"{host} · 관리자가 만든 계정",
            "token_kicker": token_kicker,
            "token_blurb": TOKEN_BLURB,
            "issued_warning": ISSUED_WARNING,
            "empty_copy": EMPTY_COPY,
            "connect_hint": CONNECT_HINT,
            "masked_token": f"{'•' * 16}{kwargs.hint}",
        }
