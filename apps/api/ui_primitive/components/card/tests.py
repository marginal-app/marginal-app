from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.card.card import Card


class CardConstructionTests(SimpleTestCase):
    def test_card_default_renders_from_named_state(self):
        example = preview_by_slug(Card, "card-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-card"', html)
        self.assertIn(example.kwargs["body"], html)

    def test_card_renders_slot_content(self):
        html = render_component("card", slots={"default": "Nested slot body"})
        self.assertIn("Nested slot body", html)
        self.assertIn('class="ds-card"', html)
        self.assertNotIn("ds-card-body", html)
