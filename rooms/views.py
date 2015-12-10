from django.shortcuts import render
from base.views import GenericTemplateView

# Create your views here.


class RoomsTemplateView(GenericTemplateView):
    """
    Base class for the views of the app "rooms".
    """

    template_path = "rooms/"
