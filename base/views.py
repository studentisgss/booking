from django.shortcuts import render
from django.views.generic import TemplateView


class GenericTemplateView(TemplateView):
    """
    Base class which extend django TemplateView.

    Every view should inherit from this class or from one of its subclass.

    template_path: the path under the templates/ directory where templates are.
                   For example: "base/".
    """

    template_path = ""

    def get_template_names(self):
        """
        Prepend the template_path to the name of the template
        """
        return [self.template_path + x
                for x in super().get_template_names()]


class BaseTemplateView(GenericTemplateView):
    """
    Base class for the views of the app "base".
    """

    template_path = "base/"
