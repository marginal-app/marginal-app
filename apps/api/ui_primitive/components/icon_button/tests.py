from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.icon_button.icon_button import IconButton


class IconButtonConstructionTests(SimpleTestCase):
    def test_default_renders_a_button_with_the_settings_gear(self):
        example = preview_by_slug(IconButton, "icon-button-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn("<button", html)
        self.assertIn('type="button"', html)
        self.assertIn('class="ds-icon-button"', html)
        self.assertIn('aria-label="설정 열기"', html)
        self.assertIn('title="설정 열기"', html)
        self.assertIn("⚙", html)
        self.assertIn('aria-hidden="true"', html)
        self.assertNotIn("is-hover", html)
        self.assertNotIn("is-focus", html)
        self.assertNotIn("<a", html)
        self.assertNotIn("href=", html)

    def test_hover_and_focus_named_states_add_modifiers(self):
        hover = preview_by_slug(IconButton, "icon-button-hover")
        focus = preview_by_slug(IconButton, "icon-button-focus")
        hover_html = render_component(hover.component, hover.kwargs)
        focus_html = render_component(focus.component, focus.kwargs)
        self.assertIn("ds-icon-button is-hover", hover_html)
        self.assertIn("ds-icon-button is-focus", focus_html)
        self.assertNotIn("is-focus", hover_html)
        self.assertNotIn("is-hover", focus_html)

    def test_href_renders_an_anchor_instead_of_a_button(self):
        html = render_component(
            "icon_button",
            {
                "label": "설정 열기",
                "icon": "⚙",
                "href": "/library/settings/",
            },
        )
        self.assertIn("<a", html)
        self.assertIn('href="/library/settings/"', html)
        self.assertIn("ds-icon-button", html)
        self.assertIn("⚙", html)
        self.assertNotIn("<button", html)

    def test_optional_attrs_pass_through_without_htmx_logic(self):
        html = render_component(
            "icon_button",
            {
                "label": "설정 열기",
                "icon": "⚙",
                "href": "/library/settings/",
                "attrs": {
                    "hx-get": "/library/settings/",
                    "hx-target": "closest .panel",
                },
            },
        )
        self.assertIn('hx-get="/library/settings/"', html)
        self.assertIn('hx-target="closest .panel"', html)
