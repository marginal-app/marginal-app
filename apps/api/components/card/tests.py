from django.test import SimpleTestCase
from django_components import registry

from components.card.examples import EXAMPLES


class CardConstructionTests(SimpleTestCase):
    def test_card_default_renders_from_named_state(self):
        example = next(row for row in EXAMPLES if row.slug == "card-default")
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertIn('class="ds-card"', html)
        self.assertIn(example.kwargs["body"], html)

    def test_card_renders_slot_content(self):
        html = registry.get("card").render(slots={"content": "Nested slot body"})
        self.assertIn("Nested slot body", html)
        self.assertIn('class="ds-card"', html)
        self.assertNotIn("ds-card-body", html)
