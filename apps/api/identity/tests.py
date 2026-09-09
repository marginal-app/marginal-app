from django.test import TestCase
from django.urls import reverse

from identity.models import ApiToken, User
from identity.tokens import DEV_TOKEN, hash_token, issue_or_rotate, seed_dev_user, user_from_bearer


class ApiTokenTests(TestCase):
    def test_hash_is_stored_not_plaintext(self):
        user = User.objects.create_user(username="dev", password="dev")
        plaintext = issue_or_rotate(user, plaintext="secret-token")
        token = ApiToken.objects.get(user=user)
        self.assertEqual(plaintext, "secret-token")
        self.assertEqual(token.key_hash, hash_token("secret-token"))
        self.assertEqual(token.hint, "oken")
        self.assertNotIn("secret-token", token.key_hash)

    def test_issue_replaces_the_only_token(self):
        user = User.objects.create_user(username="dev", password="dev")
        issue_or_rotate(user, plaintext="first-token")
        issue_or_rotate(user, plaintext="second-token")
        self.assertEqual(ApiToken.objects.filter(user=user).count(), 1)
        self.assertIsNone(user_from_bearer("first-token"))
        self.assertEqual(user_from_bearer("second-token"), user)

    def test_unknown_or_empty_bearer_is_anonymous(self):
        self.assertIsNone(user_from_bearer(""))
        self.assertIsNone(user_from_bearer("nope"))


class BearerApiTests(TestCase):
    def setUp(self):
        seed_dev_user()

    def test_ping_requires_a_bearer_token(self):
        response = self.client.get("/api/ping")
        self.assertEqual(response.status_code, 401)

    def test_ping_ok_with_seeded_token(self):
        response = self.client.get(
            "/api/ping",
            headers={"Authorization": f"Bearer {DEV_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})

    def test_ping_rejects_a_wrong_token(self):
        response = self.client.get(
            "/api/ping",
            headers={"Authorization": "Bearer wrong-token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_session_login_is_not_enough_for_api(self):
        self.client.login(username="dev", password="dev")
        response = self.client.get("/api/ping")
        self.assertEqual(response.status_code, 401)


class AccountPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dev", password="dev")

    def test_login_error_rerenders_the_form(self):
        response = self.client.post(
            reverse("identity_login"),
            {"username": "dev", "password": "nope"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "사용자 이름 또는 비밀번호가 올바르지 않습니다")

    def test_login_success_opens_token_settings(self):
        response = self.client.post(
            reverse("identity_login"),
            {"username": "dev", "password": "dev"},
        )
        self.assertRedirects(response, reverse("identity_settings"))
        settings = self.client.get(reverse("identity_settings"))
        self.assertEqual(settings.status_code, 200)
        self.assertContains(settings, "확장과 연결할 토큰이 없습니다")

    def test_settings_requires_a_session(self):
        response = self.client.get(reverse("identity_settings"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("identity_login"), response["Location"])

    def test_logout_returns_to_login(self):
        self.client.login(username="dev", password="dev")
        response = self.client.post(reverse("identity_logout"))
        self.assertRedirects(response, reverse("identity_login"))
        blocked = self.client.get(reverse("identity_settings"))
        self.assertEqual(blocked.status_code, 302)
        self.assertIn(reverse("identity_login"), blocked["Location"])

    def test_issue_shows_plaintext_once_then_only_the_hint(self):
        self.client.login(username="dev", password="dev")
        issued = self.client.post(reverse("identity_token"))
        self.assertEqual(issued.status_code, 200)
        token = ApiToken.objects.get(user=self.user)
        self.assertContains(issued, "이 토큰은 지금만 보입니다")
        self.assertContains(issued, token.hint)
        self.assertContains(issued, 'class="identity-token-plain"')
        again = self.client.get(reverse("identity_settings"))
        self.assertContains(again, f"끝자리 {token.hint}")
        self.assertNotContains(again, "이 토큰은 지금만 보입니다")
        self.assertNotContains(again, 'class="identity-token-plain"')
        self.assertEqual(ApiToken.objects.filter(user=self.user).count(), 1)
