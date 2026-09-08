from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.textarea.textarea import Textarea


class TextareaTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        example = preview_by_slug(Textarea, "textarea-empty")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-textarea", html)
        self.assertIn("is-focused", html)
        self.assertIn('placeholder="코멘트 추가..."', html)
        self.assertIn('name="comment"', html)
        self.assertNotIn("disabled", html)

    def test_filled_renders_value(self):
        example = preview_by_slug(Textarea, "textarea-filled")
        html = render_component(example.component, example.kwargs)
        self.assertIn("Draft note from a Cloud Agent", html)
        self.assertIn("ds-textarea", html)
        self.assertIn('name="comment"', html)
        self.assertNotIn("is-focused", html)
