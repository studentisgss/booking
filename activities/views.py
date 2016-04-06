from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from events.models import Event
from activities.models import Activity
from django.db.models import Q


class DetailActivityView(TemplateView):
    template_name = "activities/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity_id = kwargs["activity_id"]
        if activity_id is None:
            raise Http404
        try:
            activity = Activity.objects.get(pk=activity_id)
        except:
            raise Http404
        context["activity"] = activity
        context["events_list"] = Event.objects.filter(activity_id=activity_id)
        return context


class ListAllActivityView(TemplateView):
    template_name = "activities/listall.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num_per_page = 25
        # .filter(important=True)?
        activities_list = Activity.objects.order_by("title")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            activities_list = activities_list.filter(
                Q(title__icontains=text) | Q(description__icontains=text)
            )
        paginator = Paginator(activities_list, num_per_page)
        if "page" in kwargs:  # Number of the page to display, default 1
            page = int(kwargs["page"])
        else:
            page = 1
        try:
            activities = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page which is 1 not 0.
            activities = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            activities = paginator.page(paginator.num_pages)
        context["list"] = activities
        return context


class ListActivityView(TemplateView):
    template_name = "activities/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities_list = Activity.objects.filter(important=True).order_by("title")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            activities_list = activities_list.filter(
                Q(title__icontains=text) | Q(description__icontains=text)
            )
        context["list"] = activities_list
        return context
