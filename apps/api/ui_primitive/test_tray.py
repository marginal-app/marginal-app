from pathlib import Path

from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.tray.tray import TRAY_BODY, Tray

_CSS = Path(__file__).resolve().parent.joinpath("components/tray/tray.css").read_text()


class TrayConstructionTests(SimpleTestCase):
    def test_closed_is_off_canvas(self):
        example = preview_by_slug(Tray, "tray-closed")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-tray-host is-staged", html)
        self.assertIn('class="ds-tray"', html)
        self.assertNotIn("is-open", html)
        self.assertIn('aria-hidden="true"', html)
        self.assertIn(TRAY_BODY, html)

    def test_open_slides_in_from_the_right(self):
        example = preview_by_slug(Tray, "tray-open")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-tray-host is-staged", html)
        self.assertIn("ds-tray is-open", html)
        self.assertIn('aria-hidden="false"', html)
        self.assertIn(TRAY_BODY, html)

    def test_overlay_host_does_not_depend_on_a_parent_class(self):
        self.assertIn("position: absolute", _CSS)
        self.assertIn("inset: 0", _CSS)
        self.assertNotIn("catalog-desk", _CSS)

    def test_translate_is_the_open_motion(self):
        self.assertIn("transform: translateX(100%)", _CSS)
        self.assertIn("transform: translateX(0)", _CSS)
        self.assertIn(".ds-tray.is-open", _CSS)

    def test_slot_content_replaces_the_body_fallback(self):
        html = render_component("tray", {"open": True}, slots={"default": "Nested tray body"})
        self.assertIn("Nested tray body", html)
        self.assertIn("ds-tray is-open", html)
        self.assertNotIn("ds-tray-body", html)

    def test_open_has_kicker_and_close(self):
        example = preview_by_slug(Tray, "tray-open")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-tray-kicker", html)
        self.assertIn("페이지 · 밑줄 2", html)
        self.assertIn("ds-tray-close", html)
        self.assertIn("ds-icon--close", html)

    def test_named_states_are_desk(self):
        for slug in ("tray-closed", "tray-open"):
            self.assertEqual(preview_by_slug(Tray, slug).group, "Desk")

    def test_dismiss_is_absent_until_open_with_a_url(self):
        closed = render_component("tray", {"dismiss_url": "/catalog/"})
        open_without_url = render_component("tray", {"open": True})
        self.assertNotIn('class="ds-tray-dismiss"', closed)
        self.assertNotIn('class="ds-tray-dismiss"', open_without_url)

    def test_open_dismiss_is_an_outside_hit_target(self):
        html = render_component(
            "tray",
            {
                "open": True,
                "dismiss_url": "/catalog/",
                "dismiss_attrs": {
                    "hx-get": "/catalog/",
                    "hx-target": "#catalog-desk",
                },
            },
        )
        self.assertIn('class="ds-tray-dismiss"', html)
        self.assertIn('href="/catalog/"', html)
        self.assertIn('aria-label="닫기"', html)
        self.assertIn('hx-get="/catalog/"', html)
        self.assertIn('hx-target="#catalog-desk"', html)
