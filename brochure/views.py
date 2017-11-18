from django.views.generic import TemplateView, View
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template

import weasyprint as wp

from activities.models import Activity


class BrochurePDFView(View):
    CLASS_CHOICES = \
        [choice[0] for choice in Activity.CLASS_CHOICES if choice[0] != 'A']

    def get_context_data(self, category=None, **kwargs):
        context = {}

        # context for body
        if category in self.CLASS_CHOICES:
            activities_list = Activity.objects \
                .filter(archived = False, category = category) \
                .exclude(professor = None) \
                .order_by("title")
        else:
            activities_list = []
        context["list"] = activities_list

        # context for front page: academic year
        today = timezone.now()
        year = today.year
        if today.month < 9:
            year = year - 1
        context["academic_year"] = str(year) + "/" + str(year+1)

        # context for front page: class
        CLASS_DICT = {
            'SN': 'Natural Sciences',
            'SM': 'Moral Sciences',
            'SS': 'Social Sciences'
        }
        context["category"] = CLASS_DICT[category]
        return context

    def get(self, request, category=None, *args, **kwargs):
        if category not in self.CLASS_CHOICES:
            raise Http404
        response = HttpResponse(content_type = 'application/pdf')
        context = self.get_context_data(category=category, **kwargs)

        # body generation
        body_template = get_template('brochure/body.html')
        body_html = body_template.render(context, request)
        body_css = request.build_absolute_uri(static('css/body.css'))
        brochure = wp.HTML(string = body_html) \
            .render(stylesheets = [wp.CSS(url = body_css)])

        # front page generation
        front_template = get_template('brochure/front.html')
        front_html = front_template.render(context, request)
        front_css = request.build_absolute_uri(static('css/front.css'))
        front = wp.HTML(string = front_html, \
            base_url = request.build_absolute_uri()) \
            .render(stylesheets = [wp.CSS(url = front_css)])

        # add front page and print
        brochure.pages.insert(0, front.pages[0])
        brochure.write_pdf(target = response)

        return response
