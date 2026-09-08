from django.test import SimpleTestCase
from django_components import registry

from components.input.examples import EXAMPLES


def _example(slug: str):
    for example in EXAMPLES:
        if example.slug == slug:
            return example
    raise KeyError(slug)


class InputTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        example = _example("input-empty")
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertIn('class="ds-input"', html)
        self.assertIn('placeholder="https://my-server.example.com"', html)
        self.assertIn('value=""', html)
        self.assertNotIn("127.0.0.1", html)
        self.assertNotIn("disabled", html)

    def test_filled_renders_value(self):
        example = _example("input-filled")
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertIn('name="server_url"', html)
        self.assertIn('value="http://127.0.0.1:8000"', html)
        self.assertIn('class="ds-input"', html)
        self.assertNotIn("my-server.example.com", html)
