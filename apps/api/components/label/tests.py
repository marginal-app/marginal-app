from django.test import SimpleTestCase
from django_components import registry

from components.label.examples import EXAMPLES


def _example(slug: str):
    for example in EXAMPLES:
        if example.slug == slug:
            return example
    raise KeyError(slug)


class LabelTests(SimpleTestCase):
    def test_default_renders_text(self):
        example = _example("label-default")
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertIn('class="ds-label"', html)
        self.assertIn("ds-label-text", html)
        self.assertIn("ds-label-hint", html)
        self.assertIn("Server URL", html)
        self.assertIn("Host the extension uses to sync highlights.", html)
        self.assertNotIn(" for=", html)
