from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.sidebar.sidebar import Sidebar


class SidebarConstructionTests(SimpleTestCase):
    def test_expanded_composes_wordmark_stamp_and_account(self):
        example = preview_by_slug(Sidebar, "sidebar-expanded")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-sidebar"', html)
        self.assertNotIn("ds-sidebar--collapsed", html)
        self.assertIn("ds-wordmark--sm", html)
        self.assertIn("ds-icon--collapse", html)
        self.assertIn("검색", html)
        self.assertIn("홈", html)
        self.assertIn("라이브러리", html)
        self.assertIn("12", html)
        self.assertIn("설정", html)
        self.assertIn("ds-sync-stamp--ok", html)
        self.assertIn("SYNCED · 12:04", html)
        self.assertIn("ds-avatar", html)
        self.assertIn("malkoG", html)
        self.assertIn("127.0.0.1:8000", html)
        self.assertIn("is-active", html)
        self.assertEqual(example.group, "Primitives")

    def test_collapsed_is_the_icon_rail(self):
        example = preview_by_slug(Sidebar, "sidebar-collapsed")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-sidebar ds-sidebar--collapsed", html)
        self.assertIn("ds-sidebar__mark", html)
        self.assertNotIn("Marginal", html)
        self.assertNotIn("ds-wordmark", html)
        self.assertIn("ds-icon--expand", html)
        self.assertNotIn("ds-icon--collapse", html)
        self.assertNotIn("ds-sync-stamp", html)
        self.assertIn("ds-sidebar__sync-dot", html)
        self.assertIn("ds-avatar", html)
        self.assertNotIn("malkoG", html)
        self.assertNotIn("검색", html)

    def test_unknown_state_stays_expanded(self):
        html = render_component("sidebar", {"state": "wide"})
        self.assertIn('class="ds-sidebar"', html)
        self.assertNotIn("ds-sidebar--collapsed", html)
        self.assertIn("ds-wordmark--sm", html)
