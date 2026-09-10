from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from identity.components.token_desk.token_desk import EMPTY_COPY, TokenDesk


class TokenDeskConstructionTests(SimpleTestCase):
    def test_empty_composes_sidebar_and_issue_cta(self):
        example = preview_by_slug(TokenDesk, "identity-token-empty")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-sidebar", html)
        self.assertIn("설정", html)
        self.assertIn(EMPTY_COPY, html)
        self.assertIn("토큰 발급", html)
        self.assertIn("로그아웃", html)
        self.assertIn("http://127.0.0.1:8000", html)
        self.assertEqual(example.group, "Desk")

    def test_issued_shows_plaintext_and_copy_pill(self):
        example = preview_by_slug(TokenDesk, "identity-token-issued")
        html = render_component(example.component, example.kwargs)
        self.assertIn("dev-token-plain-k3x9", html)
        self.assertIn("방금 발급", html)
        self.assertIn("ds-pill-button", html)
        self.assertIn("복사", html)
        self.assertIn("다시 발급", html)
        self.assertEqual(example.group, "Desk")

    def test_has_masks_the_token(self):
        example = preview_by_slug(TokenDesk, "identity-token-has")
        html = render_component(example.component, example.kwargs)
        self.assertIn("끝자리 k3x9", html)
        self.assertIn("발급됨", html)
        self.assertIn("k3x9", html)
        self.assertNotIn("dev-token-plain-k3x9", html)
        self.assertEqual(example.group, "Desk")
