from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Event
from base.utils import localnow

import datetime


class ExampleView(TemplateView):
    template_name = "events/example.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_data"] = [1, 1, 2, 3, 5, 8, 13, 21]
        return context


class Agenda(TemplateView):
    template_name = "events/agenda.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "page" in kwargs:  # Number of the page to display, deafault 1 not 0
            page = int(kwargs["page"])
        else:
            page = 1
        # Display only future events
        event_list = Event.objects.filter(start__gte=localnow().date()).order_by("start")
        paginator = Paginator(event_list, 25)
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            events = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            events = paginator.page(paginator.num_pages)
        context["list"] = events
        return context


class Calendar(TemplateView):
    template_name = "events/calendar.html"
    template_name_ajax = "events/calendar_table.html"

    def get_template_names(self):
        if self.request.is_ajax():  # If the request is ajax then return only the table
            self.template_name = self.template_name_ajax
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "year" in kwargs and "month" in kwargs and "day" in kwargs:  # If a date is defined
            date = datetime.datetime(int(kwargs["year"]), int(kwargs["month"]), int(kwargs["day"]),
                                     tzinfo=timezone.get_default_timezone())
        else:
            date = localnow().date()
        context["date"] = date
        context["events"] = Event.objects.filter(start__range=(date, date + datetime.timedelta(1)))
        return context
