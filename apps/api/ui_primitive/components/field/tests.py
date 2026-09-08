from django.test import SimpleTestCase

from citry_preview.testing import render_component
from ui_primitive.components.field.preview import DEFAULT, PREVIEWS


class FieldTests(SimpleTestCase):
    def test_default_named_state_renders_label_and_input(self):
        example = PREVIEWS[0]
        html = render_component(example.component, example.kwargs)
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
