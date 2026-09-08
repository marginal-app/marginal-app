from django.test import SimpleTestCase

from ui.components.textarea.preview import PREVIEWS
from citry_components.testing import render_component


def _example(slug: str):
    for example in PREVIEWS:
        if example.slug == slug:
            return example
    raise KeyError(slug)


class TextareaTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        example = _example("textarea-empty")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-textarea", html)
        self.assertIn("is-focused", html)
        self.assertIn('placeholder="코멘트 추가..."', html)
        self.assertIn('name="comment"', html)
        self.assertNotIn("disabled", html)

    def test_filled_renders_value(self):
        example = _example("textarea-filled")
        html = render_component(example.component, example.kwargs)
        self.assertIn("Draft note from a Cloud Agent", html)
        self.assertIn("ds-textarea", html)
        self.assertIn('name="comment"', html)
        self.assertNotIn("is-focused", html)
