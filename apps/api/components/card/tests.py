from django.test import SimpleTestCase
from django_components import registry


class CardConstructionTests(SimpleTestCase):
    def test_card_renders_title_and_body(self):
        html = registry.get("card").render(
            kwargs={
                "title": "Highlight",
                "body": "Server-rendered HTML is a complete first paint.",
            },
        )
        self.assertIn('class="ds-card"', html)
        self.assertIn('class="ds-card-title"', html)
        self.assertIn("Highlight", html)
        self.assertIn('class="ds-card-body"', html)
        self.assertIn("Server-rendered HTML is a complete first paint.", html)
