from django.shortcuts import render
from base.views import BookingTemplateView

# Create your views here.


class NewsBookingTemplateView(BookingTemplateView):
    """
    Base class for the views of the app "news".
    """

    template_path = "news/"
