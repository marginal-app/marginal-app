from django_components import Component, register


@register("empty_state")
class EmptyState(Component):
    template_file = "empty_state.html"
    css_file = "empty_state.css"

    class Kwargs:
        message: str = "이 페이지에 저장된 하이라이트가 없습니다."
        hint: str = "본문을 드래그해서 하이라이트를 만들어보세요."
        icon: str = "✎"

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "message": kwargs.message,
            "hint": kwargs.hint,
            "icon": kwargs.icon,
        }
