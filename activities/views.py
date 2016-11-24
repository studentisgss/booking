from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Max, Min
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from events.models import Event
from activities.models import Activity
from activities.forms import ActivityForm


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
        context["events_list"] = Event.objects.filter(activity_id=activity_id).order_by("start")
        return context


class ListAllActivityView(TemplateView):
    template_name = "activities/listall.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities_list = Activity.objects \
            .annotate(min_start=Min("event__start")) \
            .annotate(max_end=Max("event__end")) \
            .order_by("archived", "min_start", "title")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            activities_list = activities_list.filter(
                Q(title__icontains=text) | Q(description__icontains=text)
            )
        paginator = Paginator(activities_list, per_page=25)
        page = kwargs.get("page", 1)
        try:
            activities = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page which is 1 not 0.
            activities = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            activities = paginator.page(paginator.num_pages)
        context["list"] = activities
        return context


class ListActivityView(TemplateView):
    template_name = "activities/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities_list = Activity.objects \
            .filter(archived=False) \
            .annotate(min_start=Min("event__start")) \
            .annotate(max_end=Max("event__end")) \
            .order_by("min_start", "title")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            activities_list = activities_list.filter(
                Q(title__icontains=text) | Q(description__icontains=text)
            )
        context["list"] = activities_list
        return context


class ActivityEditView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "activities/edit.html"

    permission_required = ("activities.change_activities", "rooms.can_book_room")

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
            else:
                form = ActivityForm()
        elif self.request.method == "POST":
            form = ActivityForm(self.request.POST)
        else:
            raise Http404
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        if "pk" in kwargs and kwargs["pk"]:
            try:
                activity = Activity.objects.all().get(pk=kwargs["pk"])
            except:
                raise Http404
            form = ActivityForm(request.POST, instance=activity)
            edit = True
        else:
            form = ActivityForm(request.POST)
            edit = False

        if form.is_valid():
            if edit:
                nctivity = form.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(nctivity).pk,
                    object_id=nctivity.id,
                    object_repr=str(nctivity),
                    action_flag=CHANGE
                )
            else:
                nctivity = form.save(commit=False)
                nctivity.creator = request.user
                nctivity.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(nctivity).pk,
                    object_id=nctivity.id,
                    object_repr=str(nctivity),
                    action_flag=ADDITION
                )
            return HttpResponseRedirect(reverse("activities:list"))
        else:
            return self.get(request, *args, **kwargs)


class ActivityAddView(ActivityEditView):
    permission_required = ("activities.add_activities", "rooms.can_book_room")
