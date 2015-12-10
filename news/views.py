from django.shortcuts import render
from base.views import GenericTemplateView

# Create your views here.


class NewsTemplateView(GenericTemplateView):
    """
    Base class for the views of the app "news".
    """

    template_path = "news/"
