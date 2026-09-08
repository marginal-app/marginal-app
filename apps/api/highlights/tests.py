from django.test import TestCase
from django.urls import reverse

from highlights.models import Highlight


def test_ping_requires_token(client) -> None:
    response = client.get("/api/ping")
    assert response.status_code == 401


def test_ping_ok_with_dev_token(client) -> None:
    response = client.get("/api/ping", headers={"Authorization": "Bearer dev-token"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}


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
