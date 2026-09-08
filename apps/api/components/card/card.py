from django_components import Component, register


@register("card")
class Card(Component):
    template_file = "card.html"
    css_file = "card.css"

    class Kwargs:
        body: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "body": kwargs.body,
        }
