from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.sync_stamp.sync_stamp import SyncStamp


class SyncStampConstructionTests(SimpleTestCase):
    def test_ok_is_a_printer_mark_not_a_status_chip(self):
        example = preview_by_slug(SyncStamp, "sync-stamp-ok")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-sync-stamp ds-sync-stamp--ok"', html)
        self.assertIn("ds-sync-stamp__dot", html)
        self.assertIn("SYNCED · 12:04", html)
        self.assertNotIn("status-ok", html)
        self.assertEqual(example.group, "Primitives")

    def test_syncing_and_error_keep_secondary_ink(self):
        syncing = preview_by_slug(SyncStamp, "sync-stamp-syncing")
        error = preview_by_slug(SyncStamp, "sync-stamp-error")
        syncing_html = render_component(syncing.component, syncing.kwargs)
        error_html = render_component(error.component, error.kwargs)
        self.assertIn("ds-sync-stamp--syncing", syncing_html)
        self.assertIn("SYNCING…", syncing_html)
        self.assertIn("ds-sync-stamp--error", error_html)
        self.assertIn("SYNC FAILED · 401", error_html)
        self.assertEqual(syncing.group, "Primitives")
        self.assertEqual(error.group, "Primitives")

    def test_unknown_tone_falls_back_to_ok(self):
        html = render_component("sync_stamp", {"tone": "warn", "label": "STALE"})
        self.assertIn("ds-sync-stamp--ok", html)
        self.assertNotIn("ds-sync-stamp--warn", html)
        self.assertIn("STALE", html)
