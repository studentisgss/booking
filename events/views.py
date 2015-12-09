from django.shortcuts import render
from base.views import BookingTemplateView

# Create your views here.


class EventsBookingTemplateView(BookingTemplateView):
    """
    Base class for the views of the app "events".
    """

    template_path = "events/"
