from django.shortcuts import render
from base.views import BookingTemplateView

# Create your views here.


class ActivitiesBookingTemplateView(BookingTemplateView):
    """
    Base class for the views of the app "activities".
    """

    template_path = "activities/"
