from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.widget.widget import META, PLACEHOLDER, TITLE, Widget


class WidgetConstructionTests(SimpleTestCase):
    def test_meta_shows_title_stamp_and_slot(self):
        example = preview_by_slug(Widget, "widget-meta")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-widget"', html)
        self.assertIn(TITLE, html)
        self.assertIn("ds-widget__meta", html)
        self.assertIn(META, html)
        self.assertIn("ds-widget__slot", html)
        self.assertIn(PLACEHOLDER, html)
        self.assertEqual(example.group, "Desk")

    def test_title_only_omits_the_stamp(self):
        example = preview_by_slug(Widget, "widget-title")
        html = render_component(example.component, example.kwargs)
        self.assertIn(TITLE, html)
        self.assertNotIn("ds-widget__meta", html)
        self.assertNotIn(META, html)
        self.assertIn(PLACEHOLDER, html)
        self.assertEqual(example.group, "Desk")

    def test_slot_replaces_the_placeholder(self):
        html = render_component("widget", slots={"default": "Nested slot body"})
        self.assertIn("Nested slot body", html)
        self.assertIn("ds-widget__slot", html)
        self.assertNotIn("ds-widget__placeholder", html)
