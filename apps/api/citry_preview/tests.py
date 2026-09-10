from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from citry_preview.discover import discover_previews, merge_previews
from citry_preview.preview import Preview
from citry_preview.previews import PREVIEWS
from citry_preview.testing import render_component


class ComponentRenderTests(SimpleTestCase):
    def test_empty_state_renders_without_a_view(self):
        html = render_component("empty_state")
        self.assertIn("empty-state", html)
        self.assertIn("하이라이트가 없습니다", html)

    def test_highlight_card_variants_are_kwargs_not_separate_trees(self):
        quote = render_component(
            "highlight_card",
            {
                "highlight_id": "a",
                "quote": "isolated quote",
                "color": "#f5d76e",
            },
        )
        editing = render_component(
            "highlight_card",
            {
                "highlight_id": "a",
                "quote": "isolated quote",
                "color": "#f5d76e",
                "comment": "draft",
                "editing": True,
            },
        )
        self.assertIn("isolated quote", quote)
        self.assertIn("코멘트 추가", quote)
        self.assertIn("<textarea", editing)
        self.assertIn("draft", editing)
        self.assertIn("저장", editing)

    def test_library_panel_composes_empty_and_list(self):
        empty = render_component(
            "library_panel",
            {"view": "highlights", "highlights": []},
        )
        filled = render_component(
            "library_panel",
            {
                "view": "highlights",
                "highlights": [
                    {
                        "highlight_id": "x",
                        "quote": "composed",
                        "color": "#8b8bff",
                        "comment": "",
                        "editing": False,
                        "comment_edit_url": "",
                        "comment_save_url": "",
                    }
                ],
            },
        )
        self.assertIn("empty-state", empty)
        self.assertNotIn("composed", empty)
        self.assertIn("composed", filled)
        self.assertIn("highlight-list", filled)


class PreviewCatalogTests(SimpleTestCase):
    def test_feature_slugs_still_resolve(self):
        slugs = {preview.slug for preview in PREVIEWS}
        self.assertTrue(
            {
                "empty-state",
                "highlight-card-quote",
                "highlight-card-comment",
                "highlight-card-editing",
                "highlight-list",
                "settings-idle",
                "settings-ok",
                "settings-error",
                "panel-empty",
                "panel-highlights",
                "panel-settings",
                "tray-closed",
                "tray-open",
                "catalog-desk-empty",
                "catalog-desk-idle",
                "catalog-desk-selected",
                "catalog-desk-highlights",
                "catalog-desk-comments",
                "catalog-note-empty",
                "catalog-note-filled",
                "desk-home-populated",
                "identity-login-idle",
                "identity-login-error",
                "identity-token-empty",
                "identity-token-issued",
                "identity-token-has",
            }.issubset(slugs)
        )

    def test_catalog_slugs_are_unique(self):
        slugs = [preview.slug for preview in PREVIEWS]
        self.assertEqual(slugs, list(dict.fromkeys(slugs)))

    def test_discover_previews_returns_a_list(self):
        found = discover_previews()
        self.assertIsInstance(found, list)
        self.assertTrue(all(isinstance(preview, Preview) for preview in found))

    def test_merge_previews_rejects_duplicate_slugs(self):
        row = Preview(
            slug="dup",
            title="Dup",
            description="",
            component="empty_state",
            group="Atoms",
        )
        with self.assertRaises(ValueError):
            merge_previews([row], [row])


class GalleryTests(TestCase):
    def test_gallery_lists_every_preview(self):
        response = self.client.get(reverse("component_gallery"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        for preview in PREVIEWS:
            self.assertIn(preview.title, body)
            self.assertIn(f'data-preview="{preview.slug}"', body)

    def test_each_silhouette_url_renders(self):
        for preview in PREVIEWS:
            with self.subTest(preview.slug):
                response = self.client.get(
                    reverse("component_silhouette", args=[preview.slug]),
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, preview.title)

    def test_page_silhouettes_keep_the_full_panel_frame(self):
        response = self.client.get(reverse("component_silhouette", args=["panel-empty"]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "silhouette-atom")

    def test_primitive_silhouettes_use_the_padded_atom_frame(self):
        primitives = [preview for preview in PREVIEWS if preview.group == "Primitives"]
        if not primitives:
            self.skipTest("no primitive previews discovered yet")
        response = self.client.get(
            reverse("component_silhouette", args=[primitives[0].slug]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "silhouette-atom")

    def test_desk_silhouettes_use_the_desk_frame(self):
        response = self.client.get(
            reverse("component_silhouette", args=["catalog-desk-selected"]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "silhouette-desk")
        self.assertNotContains(response, "silhouette-atom")
