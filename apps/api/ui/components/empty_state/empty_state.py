from config.citry_app import app
from citry import Component


class EmptyState(Component):
    citry = app
    name = "empty_state"
    template_file = "empty_state.citry-html"
    css_file = "empty_state.css"

    class Kwargs:
        message: str = "이 페이지에 저장된 하이라이트가 없습니다."
        hint: str = "본문을 드래그해서 하이라이트를 만들어보세요."
        icon: str = "✎"

    def template_data(self, kwargs, slots):
        return {
            "message": kwargs.message,
            "hint": kwargs.hint,
            "icon": kwargs.icon,
        }
