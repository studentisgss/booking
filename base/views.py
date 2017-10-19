from django.shortcuts import render
from django.template import RequestContext
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


def page_not_found(request):

    response = render(
        request,
        'base/404.html',
    )

    response.status_code = 404

    return response


def server_error(request):

    response = render(
        request,
        'base/500.html',
    )

    response.status_code = 500

    return response
