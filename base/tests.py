from django.test import TestCase
from base.views import GenericTemplateView
from base.utils import collect_urls
import booking.urls
from bs4 import BeautifulSoup
import exrex


class TemplatePathTest(TestCase):
    def setUp(self):
        class A(GenericTemplateView):
            pass

        class B(A):
            template_path = "template/path/"

        class C(B):
            template_name = "path/to/page.html"

        self.c_object = C()

    def test_get_template_names(self):
        """
        Test that C.get_template_names() returns the expected path
        """
        self.assertEqual(
            self.c_object.get_template_names(),
            ["template/path/path/to/page.html"]
        )


class HomeLinkTest(TestCase):
    def test_root_responses(self):
        """Test that the home page loads without errors"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_nav_links_responses(self):
        """Test that each link in the home page loads without errors"""
        response = self.client.get("/")
        soup = BeautifulSoup(response.content, "html.parser")
        nav_links = [
            tag.get("href")
            for tag in soup.find("nav").find_all("a")
            if tag.has_attr("href")
        ]

        for url in nav_links:
            response = self.client.get(url)
            self.assertIn(
                response.status_code,
                (200, 301),
                "Url {} failed".format(url)
            )


class UrlPatternTest(TestCase):
    def test_url_pattern_activities(self):
        apps = ["activities", "events", "rooms", "news"]
        for app_name in apps:
            app_module = __import__(app_name)
            for e in app_module.urls.urlpatterns:
                pattern = e.regex.pattern
                self.assertTrue(
                    pattern.startswith("^"),
                    "Url '{}' in app '{}' must start with '^'".format(
                        e.regex.pattern,
                        app_name
                    )
                )
                self.assertTrue(
                    pattern.endswith("$"),
                    "Url '{}' in app '{}' must end with '$'".format(
                        e.regex.pattern,
                        app_name
                    )
                )


class FuzzyUrlTest(TestCase):
    def setUp(self):
        # Retrieve all the url patterns used in booking
        self.url_patterns = collect_urls(booking.urls.urlpatterns)
        # For each url pattern, generate this amount of matching urls
        self.repeat = 50

    def test_url_status_code(self):
        """Generate random valid urls and test that they load without errors"""
        for url_pattern in self.url_patterns:
            for _ in range(self.repeat):
                # Generate a string that matches the url pattern
                url = "/" + "".join(map(exrex.getone, url_pattern))
                response = self.client.get(url)
                self.assertIn(
                    response.status_code,
                    (200, 301, 302, 404),
                    "Url '{}' failed with status code {}".format(
                        url,
                        response.status_code
                    )
                )
