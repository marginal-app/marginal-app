from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from identity.components.login_form.login_form import LoginForm
from identity.components.token_desk.token_desk import TokenDesk


class LoginFormConstructionTests(SimpleTestCase):
    def test_idle_has_no_error(self):
        example = preview_by_slug(LoginForm, "identity-login-idle")
        html = render_component(example.component, example.kwargs)
        self.assertIn("로그인", html)
        self.assertIn('name="username"', html)
        self.assertIn('name="password"', html)
        self.assertNotIn("올바르지 않습니다", html)

    def test_error_shows_status(self):
        example = preview_by_slug(LoginForm, "identity-login-error")
        html = render_component(example.component, example.kwargs)
        self.assertIn("사용자 이름 또는 비밀번호가 올바르지 않습니다", html)
        self.assertIn('value="dev"', html)

    def test_named_states_are_desk(self):
        for slug in ("identity-login-idle", "identity-login-error"):
            self.assertEqual(preview_by_slug(LoginForm, slug).group, "Desk")


class TokenDeskConstructionTests(SimpleTestCase):
    def test_empty_asks_to_issue(self):
        example = preview_by_slug(TokenDesk, "identity-token-empty")
        html = render_component(example.component, example.kwargs)
        self.assertIn("확장과 연결할 토큰이 없습니다", html)
        self.assertIn("토큰 발급", html)
        self.assertNotIn("다시 발급", html)
        self.assertNotIn("identity-token-plain", html)

    def test_issued_shows_plaintext_once(self):
        example = preview_by_slug(TokenDesk, "identity-token-issued")
        html = render_component(example.component, example.kwargs)
        self.assertIn("이 토큰은 지금만 보입니다", html)
        self.assertIn("dev-token-plain-k3x9", html)
        self.assertIn("다시 발급", html)

    def test_has_shows_hint_only(self):
        example = preview_by_slug(TokenDesk, "identity-token-has")
        html = render_component(example.component, example.kwargs)
        self.assertIn("끝자리 k3x9", html)
        self.assertIn("다시 발급", html)
        self.assertNotIn("이 토큰은 지금만 보입니다", html)
        self.assertNotIn("dev-token-plain-k3x9", html)

    def test_named_states_are_desk(self):
        for slug in (
            "identity-token-empty",
            "identity-token-issued",
            "identity-token-has",
        ):
            self.assertEqual(preview_by_slug(TokenDesk, slug).group, "Desk")
