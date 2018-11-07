from django.views.generic import TemplateView
from django.views import View
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Max, Min
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.dateparse import parse_time

from events.models import Event
from events.forms import EventInlineFormSet, RoomChoiceField
from activities.models import Activity
from activities.forms import ActivityForm
from rooms.models import RoomPermission, Room, Building, RoomRule
from base.utils import localnow, parse_date
from base.models import CLASS_CHOICES
from booking.settings import DATE_INPUT_FORMATS, DATE_FORMAT, TIME_FORMAT

from datetime import datetime, timedelta
from calendar import Calendar


class DetailActivityView(TemplateView):
    template_name = "activities/detail.html"

    def get_context_data(self, activity_id=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if activity_id is None:
            raise Http404
        try:
            activity = Activity.objects.get(pk=activity_id)
        except:
            raise Http404
        context["activity"] = activity
        # If the user is logged in
        if self.request.user.is_authenticated:
            # Check if the user can manage this activity
            context["can_manage_activity"] = self.request.user.has_perm(
                "activities.change_activity"
            ) and self.request.user.has_perm(
                "activities.change_" + activity.category
            )
            # Check if the user is manager only if necessary
            if not context["can_manage_activity"]:
                # User is manager if this activity is in his managed_activities
                context["is_manager"] = self.request.user.managed_activities.filter(
                    pk=activity_id
                ).exists()
        context["events_list"] = Event.objects.filter(activity_id=activity_id).order_by("start")
        return context


class ListAllActivityView(TemplateView):
    template_name = "activities/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities_list = Activity.objects \
            .annotate(min_start=Min("event__start")) \
            .annotate(max_end=Max("event__end")) \
            .order_by("archived", "category", "title", "min_start")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            activities_list = activities_list.filter(
                Q(title__icontains=text) |
                Q(description__icontains=text) |
                Q(professor__icontains=text)
            )

        if "clas" in kwargs:
            activities_list = activities_list.filter(category=kwargs["clas"])
            context["clas"] = kwargs["clas"]

        # If the user is authenticated return the activity for which he is a manager
        if self.request.user.is_authenticated:
            context["managed_activities"] = self.request.user.managed_activities.all()
            # If some of the activities are managed by the user set manages_something to True
            # I have to use set due to some problem with pagination
            context["manages_something"] = (context["managed_activities"] &
                                            activities_list).exists()

            # Set the category which the user is allowed to edit
            if self.request.user.has_perm("activities.change_activity"):
                context["managed_category"] = \
                    [c[0] for c in CLASS_CHOICES
                     if self.request.user.has_perm("activities.change_" + c[0])]
                managed_category_exists = False
                for a in activities_list:
                    if a.category in context["managed_category"]:
                        managed_category_exists = True
                        break  # Not needed to go on
                context["managed_category_exists"] = managed_category_exists

        context["list"] = activities_list
        context["all"] = True
        return context


class ListNotArchivedActivityView(ListAllActivityView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list"] = context["list"].filter(archived=False)
        context["all"] = False
        return context


class ActivityManagerEditView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "activities/edit.html"

    permission_required = ("events.change_event", "rooms.can_book_room")
    check_for_manager = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Http method
        if self.request.method == "GET":
            if "pk" in kwargs and kwargs["pk"]:
                try:
                    activity = Activity.objects.all().get(pk=kwargs["pk"])
                except:
                    raise Http404
                form = ActivityForm(instance=activity)
                events_form = EventInlineFormSet(instance=activity)
            else:
                raise Http404
        elif self.request.method == "POST":
            try:
                activity = Activity.objects.all().get(pk=kwargs["pk"])
            except:
                raise Http404
            if self.check_for_manager:                      # If the user is a manager the POST for
                form = ActivityForm(instance=activity)      # the activity will be empty, so do not
            else:                                           # use it. Otherwise use it.
                form = ActivityForm(self.request.POST, instance=activity)
            events_form = EventInlineFormSet(self.request.POST, instance=activity)
        else:
            raise Http404

        # Check if the user is a manager if required
        if self.check_for_manager:
            if not self.request.user.managed_activities.filter(pk=kwargs["pk"]).exists():
                raise PermissionDenied
            # Make activity form readonly if the user is only a manager
            for key in form.fields.keys():
                form.fields[key].widget.attrs['disabled'] = True
        # Else check if the user can manage this category
        else:
            if not self.request.user.has_perm("activities.change_" + activity.category):
                raise PermissionDenied
            # Check whether the user can change the actvity flag, if not make it read-only
            if not self.request.user.has_perm("activities.change_brochure"):
                form.fields["brochure"].widget.attrs['disabled'] = True

        # Get rooms where the user has some permission
        rooms = Room.objects.all().filter(
            roompermission__group__in=self.request.user.groups.all()
        )
        context["rooms_all"] = rooms
        # If the user is in more than one group consider only those with all permission set to 10
        rooms_waiting = Room.objects.filter(
            roompermission__group__in=self.request.user.groups.all(),
            roompermission__permission=10
        )
        # Exclude rooms for which he user has a higer permission from another group

        # THIS SIMPLE SOLUTION DOES NOT WORK ON MYSQL... So I had to use tho next one
        # rooms_waiting_exclude = Room.objects.filter(
        #     roompermission__group__in=self.request.user.groups.all(),
        #     roompermission__permission__gt=10
        # )
        # context["rooms_waiting"] = rooms_waiting.difference(rooms_waiting_exclude)

        rooms_waiting_exclude = Room.objects.filter(
            roompermission__group__in=self.request.user.groups.all(),
            roompermission__permission__gt=10
        ).values_list("id", flat=True)
        context["rooms_waiting"] = rooms_waiting.exclude(id__in=rooms_waiting_exclude).distinct()

        # Fill the choices for the rooms in the form, grouping the options by building

        for f in events_form.forms:
            room_choices = []
            for building in Building.objects.all():
                choices = []
                for room in Room.objects.filter(building=building):
                    # Add the room if the user has the permission to book or require it or
                    # if it is already be chosen
                    if (room in rooms) or (f.initial and (room.id == f.instance.room.pk)):
                        choices.append([room.id, room.get_full_name()])
                if choices:
                    room_choices.append((building.name, choices))
            # Append the empty option at the first place so it will be the default one
            room_choices = [("", "-------")] + room_choices
            f.fields["room"].choices = room_choices

        # Fill the choices of the of the empty forms only with the rooms
        # that the user can book or require
        room_choices = []
        for building in Building.objects.all():
            choices = []
            for room in Room.objects.filter(building=building):
                if room in rooms:
                    choices.append([room.id, room.get_full_name()])
            if choices:
                room_choices.append((building.name, choices))
        # Append the empty option at the first place so it will be the default one
        room_choices = [("", "-------")] + room_choices
        empty_form = events_form.empty_form
        empty_form.fields["room"].choices = room_choices

        context["form"] = form
        context["eventForm"] = events_form
        context["emptyForm"] = empty_form
        return context

    def post(self, request, *args, **kwargs):
        if "pk" in kwargs and kwargs["pk"]:
            try:
                activity = Activity.objects.all().get(pk=kwargs["pk"])
            except:
                raise Http404
            form = ActivityForm(request.POST, instance=activity)
            events_form = EventInlineFormSet(request.POST, instance=activity)
        else:
            raise Http404

        # Check if the user is a manager if required
        if self.check_for_manager:
            if not self.request.user.managed_activities.filter(pk=kwargs["pk"]).exists():
                raise PermissionDenied
        # Else check if the user can manage this category
        else:
            if not self.request.user.has_perm("activities.change_" + activity.category):
                raise PermissionDenied

        # If check_for_manager then it is not needed to check the validity of form (activity)
        # because the user has no permission to modifies it.
        if (self.check_for_manager or form.is_valid()) and events_form.is_valid():
            # Do not save the activity: managers are not allowed
            # Save the events
            instances = events_form.save(commit=False)
            with transaction.atomic():
                for i in instances:
                    # get the maximum permission for the room of the user
                    perms = []
                    for g in request.user.groups.all():
                        perms.append(i.room.get_group_perm(g))
                    perm = max(perms + [0])
                    # Set status according to permission
                    # If the permission is to require only
                    # and the user set approved the change it to waiting
                    if perm == 10:
                        if i.status == Event.APPROVED:
                            i.status = Event.WAITING
                    # If the user has no permission and modify an event
                    # set it to rejected
                    elif perm == 0:
                        i.status = Event.REJECTED
                    # Set creator and log the action
                    try:
                        new = i.creator is not None
                    except Event.creator.RelatedObjectDoesNotExist:
                        i.creator = request.user
                        new = False
                    i.save()
                    # LOG ACTION
                    LogEntry.objects.log_action(
                        user_id=self.request.user.id,
                        content_type_id=ContentType.objects.get_for_model(i).pk,
                        object_id=i.id,
                        object_repr=str(i),
                        action_flag=ADDITION if new else CHANGE
                    )
            with transaction.atomic():
                # Delete the events marked for deletion and log the actions
                for o in events_form.deleted_objects:
                    o.delete()
                    LogEntry.objects.log_action(
                        user_id=self.request.user.id,
                        content_type_id=ContentType.objects.get_for_model(o).pk,
                        object_id=o.id,
                        object_repr=str(o),
                        action_flag=DELETION
                    )
            return HttpResponseRedirect(reverse("activities:list"))
        else:
            return self.get(request, *args, **kwargs)


class ActivityEditView(ActivityManagerEditView):
    template_name = "activities/edit.html"

    permission_required = ("activities.change_activity", "rooms.can_book_room")
    check_for_manager = False

    def post(self, request, *args, **kwargs):
        # Call the super function, all check on kwargs are done so
        # we do not need to repeat them
        value = super().post(request, *args, **kwargs)
        activity = Activity.objects.all().get(pk=kwargs["pk"])
        form = ActivityForm(request.POST, instance=activity)
        events_form = EventInlineFormSet(request.POST, instance=activity)

        if form.is_valid() and events_form.is_valid():
            # Check if the brochure flag is modified and it the user has the permission
            if not self.request.user.has_perm("activities.change_brochure"):
                if "brochure" in form.changed_data:
                    raise PermissionDenied
            # Save the activity and log the change.
            # The events are saved in the parent class
            activity = form.save()
            LogEntry.objects.log_action(
                user_id=self.request.user.id,
                content_type_id=ContentType.objects.get_for_model(activity).pk,
                object_id=activity.id,
                object_repr=str(activity),
                action_flag=CHANGE
            )

        # The value to be returned is the same of the parent
        return value


class ActivityAddView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "activities.add_activity"

    template_name = "activities/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Http method
        if self.request.method == "GET":
            form = ActivityForm()
        elif self.request.method == "POST":
            form = ActivityForm(self.request.POST)
        else:
            raise Http404
            # Check if the user can change the brochure flag
        if not self.request.user.has_perm("activities.change_brochure"):
            form.fields["brochure"].widget.attrs['disabled'] = True
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        form = ActivityForm(request.POST)

        if form.is_valid():
            # Check if the brochure flag is modified and it the user has the permission
            if not self.request.user.has_perm("activities.change_brochure"):
                if "brochure" in form.changed_data:
                    raise PermissionDenied
            # Create the new activity and set the creator
            activity = form.save(commit=False)
            activity.creator = request.user
            activity.save()
            form.save_m2m()
            # Log the action
            LogEntry.objects.log_action(
                user_id=self.request.user.id,
                content_type_id=ContentType.objects.get_for_model(activity).pk,
                object_id=activity.id,
                object_repr=str(activity),
                action_flag=ADDITION
            )
            # Redirect to the edit page
            return HttpResponseRedirect(reverse("activities:edit", kwargs={"pk": activity.pk}))
        else:
            return self.get(request, *args, **kwargs)


class BookedDatesAPI(View):
    """
    This API if queried return for a given room, start and end time
    the days in which it is already booked in that time
    room_id: id of the room_id
    start: start time
    end: end time
    fromDate: date from which search, default id today - 1 month
    toDate: date to which search, default id today + 1 month
    """

    def get(self, request):
        try:
            room_id = request.GET.get("room", None)
            start = parse_time(request.GET.get("start", ""))
            end = parse_time(request.GET.get("end", ""))
            if room_id is None or start is None or end is None:
                raise Http404
            fromDate = parse_date(request.GET.get("from", ""))
            toDate = parse_date(request.GET.get("to", ""))
        except:
            raise Http404

        if fromDate is None:
            fromDate = localnow() - timedelta(days=30)
        if toDate is None:
            toDate = localnow() + timedelta(days=30)

        # Get all day in which the romm is already booked
        dates = Event.objects.all().filter(
            room_id=room_id, start__time__lt=end,
            end__time__gt=start,
            start__date__gte=fromDate, start__date__lte=toDate
        ).exclude(status=2).dates("start", "day")

        # Get day of the week in which the room is closed in that time
        days = RoomRule.objects.all().filter(Q(room_id=room_id),
                                             Q(opening_time__gt=start) | Q(closing_time__lt=end)
                                             ).only("day")

        if len(days) > 0:
            days = list(map(lambda d: d.day, days))
            closed_dates = []
            cal = Calendar()
            # First day of the month of fromDate
            start_date = fromDate.replace(day=1)

            # Until start_date is in the next month than toDate
            while start_date <= toDate:
                # For every day in which the room is closed at that time
                for d in days:
                    # Add the day to the closed ones
                    closed_dates += [w[d] for w
                                     in cal.monthdatescalendar(start_date.year, start_date.month)]
                # Go to the next month
                try:
                    start_date = start_date.replace(month=start_date.month + 1)
                except ValueError:
                    start_date = start_date.replace(year=start_date.year + 1, month=1)
            # Remove duplicate and sort
            closed_dates = list(set(closed_dates))
            closed_dates.sort()

            # Remove days before fromDate
            while closed_dates[0] < fromDate.date():
                del closed_dates[0]

            # Remove days after toDate
            while closed_dates[-1] > toDate.date():
                del closed_dates[-1]

            # Union of the dates
            dates = list(set(dates) | set(closed_dates))

        dates = [d.strftime(DATE_FORMAT) for d in dates]
        return JsonResponse(list(dates), safe=False)


class BookedHoursAPI(View):
    """
    This API if queried return for a given room and day
    the hours in which it is already booked
    room_id: id of the room_id
    day: the day to check, default today
    """

    def get(self, request):
        try:
            room_id = request.GET.get("room", None)
            day = parse_date(request.GET.get("day", ""))
        except:
            raise Http404

        if day is None:
            day = localnow().date()

        # Hours when the room is already booked
        hours = Event.objects.all().filter(
            room_id=room_id, start__date=day
        ).exclude(status=2).only("start", "end")

        # Timetable of the room if exists
        rule = RoomRule.objects.all().filter(room_id=room_id, day=day.weekday()).first()
        opening = ""
        if rule is not None:
            if rule.isClosedAllDay():
                opening = "closed"
            else:
                opening = "{} - {}".format(rule.opening_time.strftime(TIME_FORMAT),
                                           rule.closing_time.strftime(TIME_FORMAT))

        hours = ["{} - {}".format(a.start.strftime(TIME_FORMAT), a.end.strftime(TIME_FORMAT))
                 for a in hours]

        return JsonResponse({"booked": hours, "opening": opening}, safe=False)
