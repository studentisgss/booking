from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView


class BookingTemplateView(TemplateView):

    template_path = ""

    def get_template_names(self):
        return [self.template_path + x
                for x in super(BookingTemplateView, self).get_template_names()]

    def localnow():
        return timezone.localtime(timezone.now(),
                                  timezone.get_default_timezone())


class BaseBookingTemplateView(BookingTemplateView):

    template_path = "base/"
