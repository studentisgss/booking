from django.views.generic import TemplateView, View
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.core.cache import cache

import weasyprint as wp

from activities.models import Activity


class BrochurePDFView(View):
    CLASS_INITIALS = [choice[0] \
        for choice in Activity.CLASSES_WITH_TRANSLATION if choice[0] != 'A']

    CLASS_NAME = dict([(choice[0], choice[2]) \
        for choice in Activity.CLASSES_WITH_TRANSLATION if choice[0] != 'A'])

    def get_context_data(self, category=None, **kwargs):
        context = {}
        categoy = category.upper()

        # context for body
        if category in self.CLASS_INITIALS:
            activities_list = Activity.objects \
                .filter(archived=False, category=category) \
                .exclude(professor=None) \
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
        context["category"] = self.CLASS_NAME[category]
        return context

    def get(self, request, category=None, *args, **kwargs):
        category = category.upper()
        if category not in self.CLASS_INITIALS:
            raise Http404
        if cache.get(category):
            return cache.get(category)
        else:
            return self.get_pdf(request, category=category)

    def get_pdf(self, request, category=None, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        context = self.get_context_data(category=category, **kwargs)

        # body generation
        body_template = get_template('brochure/body.html')
        body_html = body_template.render(context, request)
        body_css = request.build_absolute_uri(static('brochure/css/body.css'))
        brochure = wp.HTML(string=body_html) \
            .render(stylesheets=[wp.CSS(url=body_css)])

        # index
        brochure_tree = brochure.make_bookmark_tree()
        index = [(header[0], header[1][0]+3) for header in brochure_tree]
        context["index"] = index

        # front page generation
        front_template = get_template('brochure/front.html')
        front_html = front_template.render(context, request)
        front_css = request.build_absolute_uri(static('brochure/css/front.css'))
        front = wp.HTML(string=front_html,
                        base_url=request.build_absolute_uri()) \
            .render(stylesheets=[wp.CSS(url=front_css)])

        # add front page
        brochure.pages.insert(0, front.pages[0])
        brochure.pages.insert(1, front.pages[1])

        # add metadata and print
        brochure.metadata.title = "Course catalog SGSS - Class of " \
            + self.CLASS_NAME[category]
        brochure.metadata.authors = "Scuola Galileiana di Studi Superiori"
        brochure.metadata.description = "Course catalog for the Class of " \
            + self.CLASS_NAME[category] \
            + " of the Scuola Galileiana di Studi Superiori."
        brochure.metadata.keywords = "SGSS, Galileiana, UniPD, " \
            + "course catalog, " + self.CLASS_NAME[category]
        brochure.metadata.generator = "Booking SGSS"
        today = timezone.now()
        brochure.metadata.created = str(today.date) + "/" \
            + str(today.month) + "/" + str(today.year)
        brochure.write_pdf(target=response)

        # put response in cache
        cache.set(category, response, None)

        return response
