from django.test import SimpleTestCase
from django_components import registry

from components.textarea.examples import EXAMPLES


def _example(slug: str):
    for example in EXAMPLES:
        if example.slug == slug:
            return example
    raise KeyError(slug)


class TextareaTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        example = _example("textarea-empty")
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertIn("ds-textarea", html)
        self.assertIn("is-focused", html)
        self.assertIn('placeholder="코멘트 추가..."', html)
        self.assertIn('name="comment"', html)
        self.assertNotIn("disabled", html)

    def test_filled_renders_value(self):
        example = _example("textarea-filled")
        html = registry.get(example.component).render(kwargs=example.kwargs)
        self.assertIn("Draft note from a Cloud Agent", html)
        self.assertIn("ds-textarea", html)
        self.assertIn('name="comment"', html)
        self.assertNotIn("is-focused", html)
