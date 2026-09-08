from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django_components import registry

from highlights.models import Highlight
from ui.discover import discover_examples, merge_examples
from ui.example import Example
from ui.examples import EXAMPLES, FEATURE_EXAMPLES


class ComponentRenderTests(SimpleTestCase):
    def test_empty_state_renders_without_a_view(self):
        html = registry.get("empty_state").render()
        self.assertIn("empty-state", html)
        self.assertIn("하이라이트가 없습니다", html)

    def test_highlight_card_variants_are_kwargs_not_separate_trees(self):
        quote = registry.get("highlight_card").render(
            kwargs={
                "highlight_id": "a",
                "quote": "isolated quote",
                "color": "#f5d76e",
            },
        )
        editing = registry.get("highlight_card").render(
            kwargs={
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
        empty = registry.get("library_panel").render(
            kwargs={"view": "highlights", "highlights": []},
        )
        filled = registry.get("library_panel").render(
            kwargs={
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


class ExampleCatalogTests(SimpleTestCase):
    def test_feature_slugs_still_resolve(self):
        slugs = {example.slug for example in FEATURE_EXAMPLES}
        self.assertEqual(
            slugs,
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
            },
        )

    def test_catalog_slugs_are_unique(self):
        slugs = [example.slug for example in EXAMPLES]
        self.assertEqual(slugs, list(dict.fromkeys(slugs)))

    def test_discover_examples_returns_a_list(self):
        found = discover_examples()
        self.assertIsInstance(found, list)
        self.assertTrue(all(isinstance(example, Example) for example in found))

    def test_merge_examples_rejects_duplicate_slugs(self):
        row = Example(
            slug="dup",
            title="Dup",
            description="",
            component="empty_state",
            group="Atoms",
        )
        with self.assertRaises(ValueError):
            merge_examples([row], [row])


class GalleryTests(TestCase):
    def test_gallery_lists_every_example(self):
        response = self.client.get(reverse("component_gallery"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        for example in EXAMPLES:
            self.assertIn(example.title, body)
            self.assertIn(f'data-example="{example.slug}"', body)

    def test_each_silhouette_url_renders(self):
        for example in EXAMPLES:
            with self.subTest(example.slug):
                response = self.client.get(
                    reverse("component_silhouette", args=[example.slug]),
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, example.title)

    def test_page_silhouettes_keep_the_full_panel_frame(self):
        response = self.client.get(reverse("component_silhouette", args=["panel-empty"]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "silhouette-atom")

    def test_primitive_silhouettes_use_the_padded_atom_frame(self):
        primitives = [example for example in EXAMPLES if example.group == "Primitives"]
        if not primitives:
            self.skipTest("no primitive examples discovered yet")
        response = self.client.get(
            reverse("component_silhouette", args=[primitives[0].slug]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "silhouette-atom")


class LibraryHtmxTests(TestCase):
    def test_library_seeds_demo_highlights_and_swaps_comment_card(self):
        response = self.client.get(reverse("library_highlights"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HTMX returns the same HighlightCard")

        highlight = Highlight.objects.get(
            id="22222222-2222-2222-2222-222222222222",
        )
        edit = self.client.get(
            reverse("highlight_comment", args=[highlight.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(edit.status_code, 200)
        self.assertContains(edit, "<textarea")
        self.assertContains(edit, "Review this silhouette, then merge.")

        saved = self.client.post(
            reverse("highlight_comment", args=[highlight.id]),
            {"comment": "Approved from the silhouette."},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(saved.status_code, 200)
        self.assertContains(saved, "Approved from the silhouette.")
        self.assertNotContains(saved, "<textarea")
        highlight.refresh_from_db()
        self.assertEqual(highlight.comment, "Approved from the silhouette.")

    def test_settings_htmx_swap_returns_the_same_panel(self):
        response = self.client.post(
            reverse("library_settings"),
            {"server_url": "http://127.0.0.1:8000", "api_token": "dev-token"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="panel"')
        self.assertContains(response, "연결 성공")
