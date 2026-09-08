from citry import Component, SlotInput

from config.citry_app import app


class Card(Component):
    citry = app
    name = "card"
    template_file = "card.citry-html"
    css_file = "card.css"

    class Kwargs:
        body: str = ""

    class Slots:
        default: SlotInput | None = None

    def template_data(self, kwargs, slots):
        return {
            "body": kwargs.body,
        }
