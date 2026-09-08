from django.test import SimpleTestCase
from django_components import registry


class LabelConstructionTests(SimpleTestCase):
    def test_default_renders_text_and_class(self):
        html = registry.get("label").render(
            kwargs={"text": "Server URL"},
        )
        self.assertIn("ds-label", html)
        self.assertIn("Server URL", html)
