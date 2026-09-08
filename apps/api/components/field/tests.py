from django.test import SimpleTestCase
from django_components import registry


class FieldTests(SimpleTestCase):
    def test_default_renders_label_and_input(self):
        html = registry.get("field").render(
            kwargs={
                "label": "Server URL",
                "value": "http://127.0.0.1:8000",
                "placeholder": "https://my-server.example.com",
            },
        )
        self.assertIn('class="ds-field"', html)
        self.assertIn('class="ds-field-label"', html)
        self.assertIn("Server URL", html)
        self.assertIn('class="ds-field-input"', html)
        self.assertIn('type="text"', html)
        self.assertIn('name="server_url"', html)
        self.assertIn('value="http://127.0.0.1:8000"', html)
        self.assertIn('placeholder="https://my-server.example.com"', html)
        self.assertNotIn("disabled", html)
