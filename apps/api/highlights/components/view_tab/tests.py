from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.view_tab.view_tab import ViewTab


class ViewTabConstructionTests(SimpleTestCase):
    def test_active_has_the_accent_rule(self):
        example = preview_by_slug(ViewTab, "view-tab-active")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-view-tab is-active", html)
        self.assertIn("ds-view-tab__rule", html)
        self.assertIn("목차", html)
        self.assertIn("3", html)
        self.assertEqual(example.group, "Primitives")

    def test_default_hides_the_rule(self):
        example = preview_by_slug(ViewTab, "view-tab-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-view-tab"', html)
        self.assertNotIn("is-active", html)
        self.assertNotIn("ds-view-tab__rule", html)
        self.assertEqual(example.group, "Primitives")
