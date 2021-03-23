from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from news.models import News, Message
from news.forms import NewsForm, MessageForm
from activities.models import Activity

import datetime


class NewsView(TemplateView):
    template_name = "news/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if(self.request.user.is_authenticated and
           self.request.user.has_perm('news.change_news')):
            news = News.objects.all().order_by("-start")
        else:
            # Hide, for non news.change_news users, news expired
            # from more than a week
            oneweekago = datetime.date.today() - datetime.timedelta(days=7)
            news = News.objects.filter(end__gt=oneweekago).order_by("-start")
        context["news_list"] = news
        return context


class NewsEditView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "news/edit.html"

    permission_required = "news.change_news"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Http method
        if self.request.method == "GET":
            if "pk" in kwargs and kwargs["pk"]:
                try:
                    news = News.objects.all().get(pk=kwargs["pk"])
                except:
                    raise Http404
                form = NewsForm(instance=news)
                context["edit"] = True
            else:
                form = NewsForm()
        elif self.request.method == "POST":
            if "pk" in kwargs and kwargs["pk"]:
                try:
                    news = News.objects.all().get(pk=kwargs["pk"])
                except:
                    raise Http404
                form = NewsForm(self.request.POST, instance=news)
            else:
                form = NewsForm(self.request.POST)
            context["edit"] = kwargs["edit"]
        else:
            raise Http404
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        if "pk" in kwargs and kwargs["pk"]:
            try:
                news = News.objects.all().get(pk=kwargs["pk"])
            except:
                raise Http404
            form = NewsForm(request.POST, instance=news)
            kwargs["edit"] = True
        else:
            form = NewsForm(request.POST)
            kwargs["edit"] = False

        if form.is_valid():
            if kwargs["edit"]:
                news = form.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(news).pk,
                    object_id=news.id,
                    object_repr=str(news),
                    action_flag=CHANGE
                )
            else:
                news = form.save(commit=False)
                news.creator = request.user
                news.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(news).pk,
                    object_id=news.id,
                    object_repr=str(news),
                    action_flag=ADDITION
                )
            return HttpResponseRedirect(reverse("news:news"))
        else:
            return self.get(request, *args, **kwargs)


class NewsAddView(NewsEditView):
    permission_required = "news.add_news"


class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "news/delete.html"

    permission_required = "news.delete_news"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Http method
        if "pk" in kwargs and kwargs["pk"]:
            try:
                news = News.objects.all().get(pk=kwargs["pk"])
            except:
                raise Http404
            context["news"] = news
        else:
            raise Http404
        return context

    def post(self, request, *args, **kwargs):
        if "pk" in kwargs and kwargs["pk"]:
            try:
                news = News.objects.all().get(pk=kwargs["pk"])
            except:
                raise Http404
            news.delete()
            LogEntry.objects.log_action(
                user_id=self.request.user.id,
                content_type_id=ContentType.objects.get_for_model(news).pk,
                object_id=news.id,
                object_repr=str(news),
                action_flag=DELETION
            )

        else:
            raise Http404
        return HttpResponseRedirect(reverse("news:news"))


class MessageView(TemplateView):
    template_name = "news/message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Http method
        if "activity_id" in kwargs and kwargs["activity_id"]:
            try:
                activity = Activity.objects.get(pk=kwargs["activity_id"])
            except:
                raise Http404
        else:
            raise Http404
        context["activity"] = activity
        context["messages"] = Message.objects.filter(activity_id=activity.pk).order_by("-time")
        context["can_send"] = False
        if self.request.user.is_authenticated():
            # Check permission to edit the category
            if self.request.user.has_perms(
                    ("activities.change_activity", "activities.change_" + activity.category)):
                context["can_send"] = True
            # Check if the user is a manager
            if self.request.user.managed_activities.filter(pk=activity.pk).exists():
                context["can_send"] = True

            # Create the form only if required
            if context["can_send"]:
                if "form_error" in kwargs:
                    form = MessageForm(self.request.POST)
                else:
                    form = MessageForm()
                context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        if "activity_id" in kwargs and kwargs["activity_id"]:
            try:
                activity = Activity.objects.all().get(pk=kwargs["activity_id"])
            except:
                raise Http404
        else:
            raise Http404

        # Check if the user can send Messages
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse("authentication:login"))

        # If the user has not the permission to edit this category and is not a manager: denied
        if not self.request.user.has_perms(
            ("activities.change_activity", "activities.change_" + activity.category)
        ) and not self.request.user.managed_activities.filter(pk=activity.pk).exists():
            raise PermissionDenied

        # If the user can send Messages then go on
        form = MessageForm(request.POST)
        if form.is_valid():
            mes = form.save(commit=False)
            mes.creator = request.user
            mes.activity = activity
            mes.save()
            LogEntry.objects.log_action(
                user_id=self.request.user.id,
                content_type_id=ContentType.objects.get_for_model(mes).pk,
                object_id=mes.id,
                object_repr=str(mes),
                action_flag=ADDITION
            )
            return HttpResponseRedirect(reverse("news:messages",
                                                kwargs={"activity_id": activity.pk}))
        else:
            kwargs["form_error"] = True
            return self.get(request, *args, **kwargs)
