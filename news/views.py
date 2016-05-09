from django.views.generic import TemplateView

from news.models import News


class NewsView(TemplateView):
    template_name = "news/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = News.objects.all().order_by("-start")
        context["news_list"] = news
        return context
