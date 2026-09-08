from django.test import SimpleTestCase
from django_components import registry


class InputTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        html = registry.get("input").render(
            kwargs={"placeholder": "https://my-server.example.com"},
        )
        self.assertIn('class="ds-input"', html)
        self.assertIn('placeholder="https://my-server.example.com"', html)
        self.assertNotIn("disabled", html)

    def test_filled_renders_value(self):
        html = registry.get("input").render(
            kwargs={
                "name": "server_url",
                "value": "http://127.0.0.1:8000",
            },
        )
        self.assertIn('name="server_url"', html)
        self.assertIn('value="http://127.0.0.1:8000"', html)
