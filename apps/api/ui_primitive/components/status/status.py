from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Status(Component):
    citry = app
    name = "status"
    template_file = "status.citry-html"
    css_file = "status.css"

    @dataclass
    class Kwargs:
        tone: str = "ok"
        message: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(message="연결 성공 — 저장했습니다."),
                    slug="status-ok",
                    title="Status / ok",
                    description="Success tone — connection saved.",
                ),
                meta(
                    variant(tone="error", message="연결 실패: 서버가 401로 응답했습니다"),
                    slug="status-error",
                    title="Status / error",
                    description="Error tone — ping failed.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "class_name": f"status status-{kwargs.tone}",
            "message": kwargs.message,
        }
