from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import Http404
from events.models import Event
from activities.models import Activity

# Create your views here.


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
