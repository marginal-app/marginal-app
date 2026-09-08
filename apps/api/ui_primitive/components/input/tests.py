from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.input.input import Input


class InputTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        example = preview_by_slug(Input, "input-empty")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-input"', html)
        self.assertIn('placeholder="https://my-server.example.com"', html)
        self.assertIn('value=""', html)
        self.assertNotIn("127.0.0.1", html)
        self.assertNotIn("disabled", html)

    def test_filled_renders_value(self):
        example = preview_by_slug(Input, "input-filled")
        html = render_component(example.component, example.kwargs)
        self.assertIn('name="server_url"', html)
        self.assertIn('value="http://127.0.0.1:8000"', html)
        self.assertIn('class="ds-input"', html)
        self.assertNotIn("my-server.example.com", html)
