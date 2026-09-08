from django.test import SimpleTestCase
from django_components import registry


class TextareaTests(SimpleTestCase):
    def test_empty_renders_placeholder(self):
        html = registry.get("textarea").render(
            kwargs={"placeholder": "코멘트 추가..."},
        )
        self.assertIn('class="ds-textarea"', html)
        self.assertIn('placeholder="코멘트 추가..."', html)
        self.assertIn('name="comment"', html)

    def test_filled_renders_value(self):
        html = registry.get("textarea").render(
            kwargs={"value": "Draft note from a Cloud Agent"},
        )
        self.assertIn("Draft note from a Cloud Agent", html)
