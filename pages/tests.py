from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve

from .views import HomePageView


class HomepageTests(SimpleTestCase):
    pass
    # def setUp(self):
    #     url = reverse("home")
    #     self.response = self.client.get(url)

    # # Both tests are to test if page is showing up
    # def test_url_exists_at_correct_location(self):
    #     self.assertEqual(self.response.status_code, 200)

    # # testing if correct template is used
    # def test_homepage_template(self):
    #     self.assertTemplateUsed(self.response, "home.html")

    # # testing if html contains specified text
    # def test_homepage_contains_correct_html(self):
    #     self.assertContains(self.response, "Recently returned books")

    # # testing if html does not contain specified text
    # def test_homepage_does_not_contain_incorrect_html(self):
    #     self.assertNotContains(self.response, "It's not a correct page")

    # # testing if HomePageView function resolves
    # def test_homepage_url_resolves_homepageview(self):
    #     view = resolve("/")
    #     self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)
