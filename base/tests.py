from django.test import TestCase
from django.views.generic import TemplateView
from base.views import GenericTemplateView


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
