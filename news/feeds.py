from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from news.models import News
from base.utils import localnow


class RssNewsFeed(Feed):

    def title(self):
        return "Avvisi Scuola Galileiana"

    def link(self):
        return reverse("news:news")

    def description(self):
        return "Avvisi della Scuola Galileiana di Studi Superiori"

    def items(self):
        return News.objects.filter(start__lte=localnow().date(), end__gte=localnow().date())

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return reverse("news:news")

    def item_guid(self, obj):
        return str(obj.pk)


class AtomNewsFeed(RssNewsFeed):
    feed_type = Atom1Feed

    def subtitle(self, obj):
        return "Avvisi della Scuola Galileiana di Studi Superiori"
