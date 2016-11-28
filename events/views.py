from django.views.generic import TemplateView
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.clickjacking import xframe_options_exempt
from datetime import timedelta
from calendar import monthrange
from random import shuffle
from itertools import groupby

from events.models import Event
from base.utils import localnow, default_datetime
from news.models import News


class Agenda(TemplateView):
    template_name = "events/agenda.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num_per_page = 25
        event_list = Event.objects.filter(status=0).order_by("start")
        paginator = Paginator(event_list, num_per_page)
        if "page" in kwargs:  # Number of the page to display
            page = kwargs["page"]
        else:
            now_date = localnow().replace(hour=0, minute=0, second=0, microsecond=0)
            num_past_events = event_list.filter(start__lt=now_date).count()
            page = num_past_events // num_per_page
            page += 1  # Number of pages starts from 1
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page which is 1 not 0.
            events = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            events = paginator.page(paginator.num_pages)
        context["list"] = events
        return context


class Calendar(TemplateView):
    template_name = "events/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If a date is defined
        if "year" in kwargs and "month" in kwargs and "day" in kwargs:
            try:
                year = int(kwargs["year"])
                month = int(kwargs["month"])
                day = int(kwargs["day"])
            except:
                raise Http404
            # If the year or the month are not valid the function monthrange is not invoked
            # due to shot-circuit evaluation
            if not ((year in range(1, 9999)) and (month in range(1, 12 + 1)) and
                    (day in range(1, monthrange(year, month)[1] + 1))):
                raise Http404
            date = default_datetime(year, month, day)
        else:
            date = localnow().replace(hour=0, minute=0, second=0, microsecond=0)
        context["date"] = date
        context["events"] = Event.objects.filter(
            start__range=(date, date + timedelta(1)),
            status=Event.APPROVED
        )
        return context


class Monitor(TemplateView):
    template_name = "events/monitor.html"

    def get_context_data(self, **kwargs):
        def get_event_list(items, events_per_page):
            """
            This function returns a list of list ("pages") of tuples
            (room name, list of events in room)
            where the sum of the events in each pages is not over the events_per_page
            as soon as there is not a single room with more event than thet numeber
            """
            events_grouped = groupby(items, lambda e: e.room.name)
            events_list = []
            page = []
            events_in_current_page = 0
            for room, events in events_grouped:
                list_of_events = list(events)
                if events_in_current_page == 0:  # This avoid empty page
                    page.append((room, list_of_events))
                    events_in_current_page = len(list_of_events)
                else:
                    if events_in_current_page + len(list_of_events) <= events_per_page:
                        page.append((room, list_of_events))
                        events_in_current_page += len(list_of_events)
                    else:
                        events_list.append(page)
                        page = []
                        page.append((room, list_of_events))
                        events_in_current_page = len(list_of_events)
            if page:
                events_list.append(page)
            return events_list

        context = super().get_context_data(**kwargs)
        date = localnow().replace(hour=0, minute=0, second=0, microsecond=0)
        context["date"] = date
        important_events_per_page = 6
        other_events_per_page = 1
        # Show only approved event
        # Important room
        important_events = Event.objects.filter(
            start__range=(date, date + timedelta(1)),
            status=Event.APPROVED,
            room__important=True
        ).order_by("room__name", "start")
        context["eventsImportant"] = get_event_list(
            important_events,
            important_events_per_page
        )
        context["eventsImportantIndicator"] = False if len(context["eventsImportant"]) == 1 else True
        # Other events
        other_events = Event.objects.filter(
            start__range=(date, date + timedelta(1)),
            status=Event.APPROVED,
            room__important=False
        ).order_by("room__name", "start")
        context["eventsOther"] = get_event_list(
            other_events,
            other_events_per_page
        )
        context["eventsOtherIndicator"] = False if len(context["eventsOther"]) == 1 else True
        # NEWS
        context["news"] = News.objects.filter(
            start__lte=date,
            end__gte=date,
        )
        return context

    @xframe_options_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
