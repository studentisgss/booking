from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from news.models import News
from news.forms import NewsForm


class NewsView(TemplateView):
    template_name = "news/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = News.objects.all().order_by("-start")
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
            news = form.save(commit=False)
            news.creator = request.user
            news.save()
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
        else:
            raise Http404
        return HttpResponseRedirect(reverse("news:news"))
