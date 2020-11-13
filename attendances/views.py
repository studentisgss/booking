from django.views.generic import TemplateView, View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.contrib.admin.models import LogEntry, ADDITION
from base.utils import localnow
from datetime import timedelta

from events.models import Event
from attendances.models import *
from attendances.forms import *
import datetime

import xlwt


class GalileianAttendanceRegister(TemplateView):

    template_name = "attendances/add_galileian.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if just saved banner
        if 'justsaved' in self.request.GET:
            context["justsaved_banner"] = True
        if 'detailssaved' in self.request.GET:
            context["detailssaved_banner"] = True

        context["step"] = 0   # 0: not authenticated; 1: authenticated, but without details; 2: can register

        # Check if user is authenticated
        if self.request.user.is_authenticated:
            # Check if details are available
            if hasattr(self.request.user, 'details'):
                context["step"] = 2

                # Create registration form
                if self.request.method == "GET":
                    form = GalileianAttendanceForm()
                elif self.request.method == "POST":
                    form = GalileianAttendanceForm(self.request.POST)
                else:
                    raise Http404

                # Only today lessons allowed
                date = localnow().replace(hour=0, minute=0, second=0, microsecond=0)
                form.fields["event"].queryset = Event.objects \
                    .filter(
                    start__range=(date, date + timedelta(1)),
                    status__in=(Event.APPROVED, Event.WAITING),
                    online=False
                ).order_by("start")
                context["form"] = form

            else:
                context["step"] = 1

                # Create details form
                if self.request.method == "GET":
                    form = DetailsForm()
                elif self.request.method == "POST":
                    form = DetailsForm(self.request.POST)
                else:
                    raise Http404
                context["form"] = form

        return context

    def post(self, request, *args, **kwargs):
        # Check if authenticated
        if request.user.is_authenticated:
            # Check if details are available
            if hasattr(request.user, 'details'):
                # Check validity of registration form
                form = GalileianAttendanceForm(request.POST)
                if form.is_valid():
                    # Create the new attendance and set the user
                    attendance = form.save(commit=False)
                    attendance.user = request.user
                    attendance.save()
                    form.save_m2m()
                    # Redirect to initial page, with success banner
                    return HttpResponseRedirect(reverse("attendances:register") + "?justsaved")
            else:
                # Check validity of details form
                form = DetailsForm(request.POST)
                if form.is_valid():
                    # Create the new details and set the user
                    details = form.save(commit=False)
                    details.user = request.user
                    details.save()
                    form.save_m2m()
                    # Redirect to initial page, with success banner
                    return HttpResponseRedirect(reverse("attendances:register") + "?detailssaved")
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
        date = localnow().replace(hour=0, minute=0, second=0, microsecond=0)
        form.fields["event"].queryset = Event.objects \
            .filter(
            start__range=(date, date + timedelta(1)),
            status__in=(Event.APPROVED, Event.WAITING),
            online=False
        ).order_by("start")
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        form = ForeignAttendanceForm(request.POST)

        if form.is_valid():
            # Create the new presence and save
            form.save()
            # Redirect to initial page, with success banner
            return HttpResponseRedirect(reverse("attendances:register") + "?justsaved")
        else:
            return self.get(request, *args, **kwargs)


class ExtractData(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):

    template_name = "attendances/extract_data.html"
    permission_required = "attendances.get_attendances_data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lessons with presences list
        events = Event.objects.annotate(num_presences=Count('galileianattendance') + Count('foreignattendance')) \
            .order_by('-start') \
            .filter(num_presences__gt=0)
        context["list"] = events

        # Errors
        if 'generic_error' in self.request.GET:
            context["generic_error"] = True
        if 'date_ordering_error' in self.request.GET:
            context["date_ordering_error"] = True
        if 'no_events' in self.request.GET:
            context["no_events"] = True

        # Form
        context["form"] = ExtractPeriodForm()

        return context


class Extract(LoginRequiredMixin, PermissionRequiredMixin, View):

    permission_required = "attendances.get_attendances_data"

    def get(self, request, event, *args, **kwargs):
        try:
            event = Event.objects.get(pk=event)
        except Event.DoesNotExist:
            raise Http404
        filename = event.start.strftime('%Y_%m_%d_') + event.activity.title.replace(' ', '_')
        return self.get_xls([event], filename)

    def post(self, request, *args, **kwargs):
        form = ExtractPeriodForm(request.POST)

        if form.is_valid():
            # Get dates
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if end_date < start_date:
                return HttpResponseRedirect(reverse("attendances:extract_data") + "?date_ordering_error")

            # Extract all events in the period
            events = Event.objects.filter(start__lt=end_date + datetime.timedelta(days=1), start__gt=start_date)
            if len(events) == 0:
                return HttpResponseRedirect(reverse("attendances:extract_data") + "?no_events")

            # Return excel file
            filename = start_date.strftime('%Y_%m_%d_') + end_date.strftime('%Y_%m_%d_')
            return self.get_xls(events, filename)
        else:
            return HttpResponseRedirect(reverse("attendances:extract_data") + "?generic_error")

    def get_xls(self, events, filename):
        # Create .xls file from list of events

        # Compute accademic year from first event
        if events[0].start.month < 9:
            accademic_year = str(events[0].start.year - 1) + "/" + str(events[0].start.year)
        else:
            accademic_year = str(events[0].start.year) + "/" + str(events[0].start.year + 1)

        # Create file
        datafile = HttpResponse(content_type='application/ms-excel')
        datafile['Content-Disposition'] = 'attachment; filename="' + filename + '.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Presenze')

        # Heading
        ws.write_merge(0, 0, 0, 7, 'Scuola Galileiana di Studi Superiori ' + accademic_year,
                       xlwt.easyxf("pattern: pattern solid, fore_color yellow; font: bold True; align: horiz center"))

        header_font = xlwt.XFStyle()
        header_font.font.bold = True
        columns = ['Cognome', 'Nome', 'Matricola', 'E-mail', 'Corso', 'Data e orario lezione', 'Aula', 'Posto']

        for col_num in range(len(columns)):
            ws.write(1, col_num, columns[col_num], header_font)
        row_num = 1

        # Cycle on each event
        for event in events:
            galileian_attendances = GalileianAttendance.objects \
                .filter(event=event)
            foreign_attendances = ForeignAttendance.objects \
                .filter(event=event)

            # Galileian attendances
            galileian_font = xlwt.XFStyle()

            for g in galileian_attendances:
                row_num += 1
                ws.write(row_num, 0, g.user.last_name, galileian_font)
                ws.write(row_num, 1, g.user.first_name, galileian_font)
                ws.write(row_num, 2, g.user.details.matricola, galileian_font)
                ws.write(row_num, 3, g.user.email, galileian_font)
                ws.write(row_num, 4, g.event.activity.title, galileian_font)
                ws.write(row_num, 5, g.event.start.strftime('%d/%m/%Y %h:%m-') + g.event.end.strftime('%h:%m'), galileian_font)
                ws.write(row_num, 6, g.event.room.name + "(" + g.event.room.building.name + ")", galileian_font)
                ws.write(row_num, 7, g.chair, galileian_font)

            # Foreign attendances
            foreign_font = xlwt.XFStyle()
            foreign_font.font.italic = True

            for g in foreign_attendances:
                row_num += 1
                ws.write(row_num, 0, g.last_name, foreign_font)
                ws.write(row_num, 1, g.first_name, foreign_font)
                ws.write(row_num, 2, g.matricola, foreign_font)
                ws.write(row_num, 3, g.email, foreign_font)
                ws.write(row_num, 4, g.event.activity.title, foreign_font)
                ws.write(row_num, 5, g.event.start.strftime('%d/%m/%Y %h:%m-') + g.event.end.strftime('%h:%m'), foreign_font)
                ws.write(row_num, 6, g.event.room.name + "(" + g.event.room.building.name + ")", foreign_font)
                ws.write(row_num, 7, g.chair, foreign_font)

            # Log action
            ExtractionLog(
                user=self.request.user,
                event=event
            ).save()

        wb.save(datafile)

        return datafile
