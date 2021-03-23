from django.core import management
from django.shortcuts import render
from django.template import RequestContext
from django.views.generic import TemplateView, View
from django.core.management.base import CommandError
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from base.forms import UserFileForm, GroupMembersForm
from booking.settings import BACKUP_COMMAND
import subprocess


class GenericTemplateView(TemplateView):
    """
    Base class which extend django TemplateView.

    Every view should inherit from this class or from one of its subclass.

    template_path: the path under the templates/ directory where templates are.
                   For example: "base/".
    """

    template_path = ""

    def get_template_names(self):
        """
        Prepend the template_path to the name of the template
        """
        return [self.template_path + x
                for x in super().get_template_names()]


def page_not_found(request):

    response = render(
        request,
        'base/404.html',
    )

    response.status_code = 404

    return response


def server_error(request):

    response = render(
        request,
        'base/500.html',
    )

    response.status_code = 500

    return response


class ManagementView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "base/manage.html"

    permission_required = ("auth.add_user", "auth.change_user", "auth.delete_user",
                           "activities.change_activity", "activities.change_brochure")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["backup"] = BACKUP_COMMAND is not None
        if self.request.method == "POST" and "user_file_success" not in kwargs:
            context["form"] = UserFileForm(self.request.POST, self.request.FILES)
        else:
            context["form"] = UserFileForm()
            if "user_file_success" in kwargs:
                context["user_file_alert"] = True
                context["user_file_success"] = kwargs.get("user_file_success", False)
                context["user_file_error"] = kwargs.get("user_file_error", None)
            if "clean_users_success" in self.request.session:
                context["clean_users_alert"] = True
                context["clean_users_success"] = self.request.session.pop(
                    "clean_users_success", False
                )
                context["clean_users_error"] = self.request.session.pop("clean_users_error", None)
            if "clean_activities_success" in self.request.session:
                context["clean_activities_alert"] = True
                context["clean_activities_success"] = self.request.session.pop(
                    "clean_activities_success", False
                )
                context["clean_activities_error"] = self.request.session.pop("clean_activities_error", None)
            if "backup_success" in self.request.session:
                context["backup_alert"] = True
                context["backup_success"] = self.request.session.pop("backup_success", False)
                context["backup_message"] = self.request.session.pop("backup_message", None)
        return context

    def post(self, request, *args, **kwargs):
        form = UserFileForm(request.POST, request.FILES)
        if form.is_valid():
            kwargs["user_file_success"] = True
            f = request.FILES["user_file"]
            # Call the management command
            try:
                management.call_command("updateusers", f.temporary_file_path())
            except CommandError as e:
                kwargs["user_file_success"] = False
                kwargs["user_file_error"] = str(e)
        return self.get(request, *args, **kwargs)


class CleanUserView(LoginRequiredMixin, PermissionRequiredMixin, View):

    permission_required = ("auth.add_user", "auth.change_user", "auth.delete_user")

    def get(self, *args, **kwargs):
        self.request.session["clean_users_success"] = True
        try:
            management.call_command("clearinactiveusers")
        except CommandError as e:
            self.request.session["clean_users_success"] = False
            self.request.session["clean_users_error"] = str(e)
        return HttpResponseRedirect(reverse("base:management"))


class CleanActivitiesView(LoginRequiredMixin, PermissionRequiredMixin, View):

    permission_required = ("activities.change_activity", "activities.change_brochure")

    def get(self, *args, **kwargs):
        self.request.session["clean_activities_success"] = True
        try:
            management.call_command("cleanactivities")
        except CommandError as e:
            self.request.session["clean_activities_success"] = False
            self.request.session["clean_activities_error"] = str(e)
        return HttpResponseRedirect(reverse("base:management"))


class BackupView(LoginRequiredMixin, PermissionRequiredMixin, View):

    permission_required = ("auth.add_user", "auth.change_user", "auth.delete_user")

    def get(self, *args, **kwargs):
        self.request.session["backup_success"] = True
        output = ""
        try:
            output = subprocess.check_output(BACKUP_COMMAND, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.request.session["backup_success"] = False
            output = e.output
        except PermissionError as e:
            self.request.session["backup_success"] = False
            output = "  Permessi non sufficienti per eseguire il comando. "
        self.request.session["backup_message"] = str(output).replace("\\n", "\n")[2:-1]
        return HttpResponseRedirect(reverse("base:management"))


class GroupsMembersView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "base/groups.html"

    permission_required = ("auth.change_group",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_forms = []
        # For every group create the forms to add and remove the users
        # If there was any error there will be `add_error` or `remove_error` in kwargs
        # with the id of the relative group
        for g in Group.objects.all():
            entry = {
                "group": g,
                "add": GroupMembersForm(g, True, self.request.POST) if "add_error" in kwargs and
                kwargs["add_error"] == g.pk else GroupMembersForm(g),
                "remove": GroupMembersForm(g, False, self.request.POST)
                if "remove_error" in kwargs and kwargs["remove_error"] == g.pk
                else GroupMembersForm(g, False),
                "members": g.user_set.all().order_by("first_name", "last_name")
            }
            group_forms.append(entry)
        context["group_forms"] = group_forms
        return context

    def get(self, *args, **kwargs):
        # Remove a single user
        if "user" in self.request.GET:
            if "pk" not in kwargs:
                raise Http404
            try:
                group = Group.objects.get(pk=kwargs["pk"])
                user = group.user_set.get(pk=self.request.GET["user"])
            except (Group.DoesNotExist, User.DoesNotExist):
                raise Http404
            group.user_set.remove(user)

        # Clear the inactive users in the group (the pk is in kwargs by the url definition)
        if "operation" in kwargs and kwargs["operation"] == "clear":
            try:
                group = Group.objects.get(pk=kwargs["pk"])
            except (Group.DoesNotExist, User.DoesNotExist):
                raise Http404
            inactive = group.user_set.filter(is_active=False)
            group.user_set.remove(*inactive)

        return super().get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Operation identifies what request was made
        if "operation" not in kwargs or "pk" not in kwargs:
            raise Http404

        try:
            group = Group.objects.get(pk=kwargs["pk"])
        except Group.DoesNotExist:
            raise Http404

        if kwargs["operation"] == "add":
            form = GroupMembersForm(group, True, request.POST)
            if form.is_valid():
                group.user_set.add(*form.cleaned_data["members"])
            else:
                # Set the error key in kwargs
                kwargs["add_error"] = group.pk
            return self.get(request, *args, **kwargs)

        elif kwargs["operation"] == "remove":
            form = GroupMembersForm(group, False, request.POST)
            if form.is_valid():
                group.user_set.remove(*form.cleaned_data["members"])
            else:
                # Set the error key in kwargs
                kwargs["remove_error"] = group.pk
            return self.get(request, *args, **kwargs)

        else:
            raise Http404


class About(TemplateView):
    template_name = "base/about.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
