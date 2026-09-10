from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from identity.components.login_form.login_form import ERROR_MESSAGE, LoginForm


class LoginFormConstructionTests(SimpleTestCase):
    def test_idle_is_a_wordmark_sheet(self):
        example = preview_by_slug(LoginForm, "identity-login-idle")
        html = render_component(example.component, example.kwargs)
        self.assertIn("identity-login", html)
        self.assertIn("ds-wordmark", html)
        self.assertIn("로그인", html)
        self.assertIn("사용자 이름", html)
        self.assertNotIn("ds-sync-stamp", html)
        self.assertIn('type="submit"', html)
        self.assertEqual(example.group, "Desk")

    def test_error_uses_sync_stamp_not_status(self):
        example = preview_by_slug(LoginForm, "identity-login-error")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-sync-stamp--error", html)
        self.assertIn(ERROR_MESSAGE, html)
        self.assertIn("is-invalid", html)
        self.assertIn('value="dev"', html)
        self.assertNotIn("ds-status", html)
        self.assertEqual(example.group, "Desk")
