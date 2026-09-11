from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from highlights.components.catalog_note.catalog_note import SAVE_ERROR
from highlights.models import Catalog, CatalogMembership, Highlight
from identity.tokens import seed_dev_user


class LibraryHtmxTests(TestCase):
    def setUp(self):
        seed_dev_user()
        self.client.login(username="dev", password="dev")

    def test_library_list_requires_a_session(self):
        self.client.logout()
        response = self.client.get(reverse("library_highlights"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("identity_login"), response["Location"])

    def test_library_settings_stays_open(self):
        self.client.logout()
        response = self.client.get(reverse("library_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API Token")

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

    def test_settings_rejects_an_unknown_token(self):
        response = self.client.post(
            reverse("library_settings"),
            {"server_url": "http://127.0.0.1:8000", "api_token": "wrong-token"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "연결 실패")
        self.assertContains(response, "서버가 401로 응답했습니다")


class CatalogDeskHtmxTests(TestCase):
    def setUp(self):
        seed_dev_user()
        self.client.login(username="dev", password="dev")

    def test_catalog_requires_a_session(self):
        self.client.logout()
        response = self.client.get(reverse("catalog_desk"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("identity_login"), response["Location"])

    def test_catalog_lists_seeded_pages(self):
        response = self.client.get(reverse("catalog_desk"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hypothesis")
        self.assertContains(response, "Item 321")
        self.assertContains(response, 'class="ds-tray"')
        self.assertNotContains(response, "ds-tray is-open")

    def test_catalog_does_not_list_another_users_page(self):
        other = seed_dev_user(username="other", token="other-token")
        catalog = Catalog.get_or_create_from_page_key("https://secret.example/page")
        CatalogMembership.objects.create(user=other, catalog=catalog, title="Secret")
        response = self.client.get(reverse("catalog_desk"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hypothesis")
        self.assertNotContains(response, "Secret")

    def test_clicking_a_row_swaps_the_desk_with_the_tray_open(self):
        self.client.get(reverse("catalog_desk"))
        catalog = Catalog.objects.get(path="/hypothesis")
        response = self.client.get(
            reverse("catalog_desk_detail", args=[catalog.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="catalog-desk"')
        self.assertContains(response, "ds-tray is-open")
        self.assertContains(response, "HTMX returns the same HighlightCard")
        self.assertContains(response, "페이지 노트")
        self.assertContains(response, "catalog-note__read")
        self.assertContains(response, "✎")
        self.assertNotContains(response, "<textarea")
        self.assertContains(
            response,
            "SSR 실루엣은 이 페이지 노트에서 리뷰한다",
        )
        self.assertContains(response, "is-selected")
        self.assertContains(response, 'class="ds-tray-dismiss"')
        self.assertContains(response, 'hx-get="/catalog/"')

    def test_dismiss_returns_the_idle_desk(self):
        self.client.get(reverse("catalog_desk"))
        catalog = Catalog.objects.get(path="/hypothesis")
        self.client.get(
            reverse("catalog_desk_detail", args=[catalog.id]),
            HTTP_HX_REQUEST="true",
        )
        response = self.client.get(
            reverse("catalog_desk"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="catalog-desk"')
        self.assertContains(response, "Hypothesis")
        self.assertNotContains(response, "ds-tray is-open")
        self.assertNotContains(response, 'class="ds-tray-dismiss"')

    def test_catalog_note_edit_save_and_cancel(self):
        self.client.get(reverse("catalog_desk"))
        catalog = Catalog.objects.get(path="/hypothesis")
        membership = CatalogMembership.objects.get(user__username="dev", catalog=catalog)
        note_url = reverse("catalog_note", args=[catalog.id])

        edit = self.client.get(note_url, HTTP_HX_REQUEST="true")
        self.assertEqual(edit.status_code, 200)
        self.assertContains(edit, "<textarea")
        self.assertContains(edit, "저장")
        self.assertContains(edit, "취소")
        self.assertContains(edit, "SSR 실루엣은 이 페이지 노트에서 리뷰한다")
        self.assertNotContains(edit, "✎")

        canceled = self.client.post(
            note_url,
            {"note": "이 초안은 버려져야 한다.", "cancel": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(canceled.status_code, 200)
        self.assertContains(canceled, "catalog-note__read")
        self.assertContains(canceled, "SSR 실루엣은 이 페이지 노트에서 리뷰한다")
        self.assertNotContains(canceled, "<textarea")
        membership.refresh_from_db()
        self.assertIn("SSR 실루엣은 이 페이지 노트에서 리뷰한다", membership.note)

        saved = self.client.post(
            note_url,
            {"note": "트레이에서 저장한 페이지 노트."},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(saved.status_code, 200)
        self.assertContains(saved, "트레이에서 저장한 페이지 노트.")
        self.assertContains(saved, "catalog-note__read")
        self.assertNotContains(saved, "<textarea")
        membership.refresh_from_db()
        self.assertEqual(membership.note, "트레이에서 저장한 페이지 노트.")

    def test_catalog_note_save_failure_stays_in_edit(self):
        self.client.get(reverse("catalog_desk"))
        catalog = Catalog.objects.get(path="/hypothesis")
        note_url = reverse("catalog_note", args=[catalog.id])
        with patch.object(CatalogMembership, "save", side_effect=RuntimeError("nope")):
            failed = self.client.post(
                note_url,
                {"note": "이 저장은 실패한다."},
                HTTP_HX_REQUEST="true",
            )
        self.assertEqual(failed.status_code, 200)
        self.assertContains(failed, "<textarea")
        self.assertContains(failed, "이 저장은 실패한다.")
        self.assertContains(failed, SAVE_ERROR)
        self.assertContains(failed, "저장")
        self.assertNotContains(failed, "✎")
