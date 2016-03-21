from django.test import TestCase
from base.views import GenericTemplateView
from bs4 import BeautifulSoup


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
    def test_link_responses(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "lxml")
        links = [
            tag.get("href")
            for tag in soup.find_all("a")
            if tag.has_attr("href")
        ]

        for url in links:
            response = self.client.get(url)
            self.assertIn(
                response.status_code,
                (200, 301),
                "Url {} failed".format(url)
            )
