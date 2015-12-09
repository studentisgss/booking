from django.shortcuts import render
from base.views import BookingTemplateView

# Create your views here.


class RoomsBookingTemplateView(BookingTemplateView):
    """
    Base class for the views of the app "rooms".
    """

    template_path = "rooms/"
