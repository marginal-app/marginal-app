from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.home_desk.home_desk import HEADLINE, KICKER, QUOTE, HomeDesk
from identity.tokens import seed_dev_user


class HomeDeskConstructionTests(SimpleTestCase):
    def test_populated_composes_sidebar_widgets_and_bars(self):
        example = preview_by_slug(HomeDesk, "desk-home-populated")
        html = render_component(example.component, example.kwargs)
        self.assertIn("home-desk", html)
        self.assertIn("ds-sidebar", html)
        self.assertIn(KICKER, html)
        self.assertIn(HEADLINE, html)
        self.assertIn("위젯 편집", html)
        self.assertIn("이번 주", html)
        self.assertIn("지난주 대비 +9", html)
        self.assertIn("home-week__bar", html)
        self.assertIn(QUOTE, html)
        self.assertIn("ds-marginalia", html)
        self.assertIn("자주 돌아간 페이지", html)
        self.assertIn("Why Server-Rendered HTML Still Wins", html)
        self.assertIn("Item 321", html)
        self.assertIn("+ 위젯 추가", html)
        self.assertNotIn("ds-widget__placeholder", html)
        self.assertEqual(example.group, "Desk")


class HomeDeskViewTests(TestCase):
    def test_home_requires_a_session(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("identity_login"), response["Location"])

    def test_home_renders_the_populated_desk(self):
        seed_dev_user()
        self.client.login(username="dev", password="dev")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home-desk")
        self.assertContains(response, "이번 주 밑줄")
        self.assertContains(response, "+ 위젯 추가")
