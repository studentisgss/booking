from django.views.generic import TemplateView, View
from django.http import Http404, HttpResponse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template

import weasyprint as wp

from activities.models import Activity


class BrochurePDFView(View):
    CLASS_CHOICES = \
        [choice[0] for choice in Activity.CLASS_CHOICES if choice[0] != 'A']

    def get_context_data(self, category=None, **kwargs):
        context = {}
        if category in self.CLASS_CHOICES:
            activities_list = Activity.objects \
                .filter(archived = False, category = category) \
                .exclude(professor = None) \
                .order_by("title")
        else:
            activities_list = []
        context["list"] = activities_list
        return context

    def get(self, request, category=None, *args, **kwargs):
        if category not in self.CLASS_CHOICES:
            raise Http404
        response = HttpResponse(content_type = 'application/pdf')
        context = self.get_context_data(category=category, **kwargs)

        body_template = get_template('brochure/body.html')
        body_html = body_template.render(context, request)

        body_css = request.build_absolute_uri(static('brochure/body.css'))
        brochure = wp.HTML(string = body_html) \
            .render(stylesheets = [wp.CSS(url = body_css)])
        brochure.write_pdf(target = response)
        return response
