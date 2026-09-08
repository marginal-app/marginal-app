from django.test import SimpleTestCase
from django_components import registry

from components.field.examples import DEFAULT, EXAMPLES


class FieldTests(SimpleTestCase):
    def test_default_named_state_renders_label_and_input(self):
        example = EXAMPLES[0]
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertEqual(example.slug, "field-default")
        self.assertEqual(example.group, "Primitives")
        self.assertEqual(example.kwargs, DEFAULT)
        self.assertIn('class="ds-field"', html)
        self.assertIn('class="ds-field-label"', html)
        self.assertIn('class="ds-field-input"', html)
        self.assertIn("Server URL", html)
        self.assertIn('type="text"', html)
        self.assertIn('name="server_url"', html)
        self.assertIn('value="http://127.0.0.1:8000"', html)
        self.assertIn('placeholder="https://my-server.example.com"', html)
        self.assertNotIn("disabled", html)
