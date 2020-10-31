from django.views.generic import TemplateView, View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.core.cache import cache

from events.models import Event
from attendances.forms import *

import logging
logger = logging.getLogger(__name__)


class GalileianAttendanceRegister(TemplateView):

    template_name = "attendances/add_galileian.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if just saved banner
        if kwargs['justsaved'] == '1':
            context["justsaved_banner"] = True
        elif kwargs['justsaved'] == '2':
            context["phonesaved_banner"] = True

        context["step"] = 0   # 0: not authenticated; 1: authenticated, but without phone; 2: can register

        # Check if user is authenticated
        if self.request.user.is_authenticated:
            # Check if phone number is available
            if hasattr(self.request.user, 'phone'):
                context["step"] = 2

                # Create registration form
                if self.request.method == "GET":
                    form = GalileianAttendanceForm()
                elif self.request.method == "POST":
                    form = GalileianAttendanceForm(self.request.POST)
                else:
                    raise Http404

                # Only today lessons allowed
                t = timezone.now()
                form.fields["event"].queryset = Event.objects \
                    .filter(online=False, start__year = t.year, start__month = t.month, start__day = t.day) \
                    .order_by("start")
                context["form"] = form

            else:
                context["step"] = 1

                # Create cell number form
                if self.request.method == "GET":
                    form = PhoneForm()
                elif self.request.method == "POST":
                    form = PhoneForm(self.request.POST)
                else:
                    raise Http404
                context["form"] = form

        return context

    def post(self, request, *args, **kwargs):
        # Check if authenticated
        if request.user.is_authenticated:
            # Check if phone number is available
            if hasattr(request.user, 'phone'):
                # Check validity of registration form
                form = GalileianAttendanceForm(request.POST)
                if form.is_valid():
                    # Create the new attendance and set the user
                    attendance = form.save(commit=False)
                    attendance.user = request.user
                    attendance.save()
                    form.save_m2m()
                    # Redirect to initial page, with success banner
                    return HttpResponseRedirect(reverse("attendances:register", kwargs={"justsaved": 1}))
            else:
                # Check validity of phone number form
                form = PhoneForm(request.POST)
                if form.is_valid():
                    # Create the new cell number and set the user
                    cellrecord = form.save(commit=False)
                    cellrecord.user = request.user
                    cellrecord.save()
                    form.save_m2m()
                    # Redirect to initial page, with success banner
                    return HttpResponseRedirect(reverse("attendances:register", kwargs={"justsaved": 2}))
        return self.get(request, *args, **kwargs)


class ForeignAttendanceRegister(TemplateView):

    template_name = "attendances/add_foreign.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Http method
        if self.request.method == "GET":
            form = ForeignAttendanceForm()
        elif self.request.method == "POST":
            form = ForeignAttendanceForm(self.request.POST)
        else:
            raise Http404

        # Only today lessons allowed
        t = timezone.now()
        form.fields["event"].queryset = Event.objects \
            .filter(online=False, start__year = t.year, start__month = t.month, start__day = t.day) \
            .order_by("start")
        context["form"] = form
        return context

    
    def post(self, request, *args, **kwargs):
        form = ForeignAttendanceForm(request.POST)

        if form.is_valid():
            # Create the new presence and save
            presence = form.save()
            # Redirect to initial page, with success banner
            return HttpResponseRedirect(reverse("attendances:register", kwargs={"justsaved": 1}))
        else:
            return self.get(request, *args, **kwargs)