from django.shortcuts import render
from base.views import GenericTemplateView

# Create your views here.


class EventsTemplateView(GenericTemplateView):
    """
    Base class for the views of the app "events".
    """

    template_path = "events/"
