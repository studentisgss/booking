from django.shortcuts import render
from base.views import GenericTemplateView

# Create your views here.


class ActivitiesTemplateView(GenericTemplateView):
    """
    Base class for the views of the app "activities".
    """

    template_path = "activities/"
