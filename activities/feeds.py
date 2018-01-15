from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from django.http import Http404
from events.models import Event
from news.models import News, Message
from activities.models import Activity
from base.utils import localnow
from booking.settings import TIME_ZONE


class RssActivityFeed(Feed):

    description_template = "activities/feed/description.html"

    def get_object(self, request, activity_id):
        try:
            return Activity.objects.get(pk=activity_id)
        except (Activity.DoesNotExist, OverflowError):
            raise Http404

    def title(self, obj):
        return "Attività Scuola Galileiana"

    def link(self, obj):
        return reverse("events:calendar")

    def description(self, obj):
        return "Attività della Scuola Galileiana di Studi Superiori"

    def items(self, obj):
        return list(Event.objects.filter(activity=obj, start__date=localnow().date(), status=0)) + \
            list(News.objects.filter(start__lte=localnow().date(), end__gte=localnow().date())) + \
            list(Message.objects.filter(activity=obj))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(kwargs["item"], Event):
            context["type"] = "event"
        elif isinstance(kwargs["item"], News):
            context["type"] = "news"
        elif isinstance(kwargs["item"], Message):
            context["type"] = "message"
        else:
            raise Http404
        return context

    def item_title(self, item):
        if isinstance(item, Event):
            return item.activity.get_full_title()
        elif isinstance(item, News):
            return item.title
        elif isinstance(item, Message):
            return item.title
        else:
            raise Http404

    def item_link(self, item):
        if isinstance(item, Event):
            return reverse("activities:details", kwargs={"activity_id": item.activity_id})
        elif isinstance(item, News):
            return reverse("news:news")
        elif isinstance(item, Message):
            return "mailto:%s" % item.creator.email
        else:
            raise Http404

    def item_guid(self, item):
        # Unique identifier of the feed's item
        if isinstance(item, Event):
            return str(item.pk) + str(item.room.pk) + \
                item.start.strftime("%H%M") + item.end.strftime("%H%M")
        elif isinstance(item, News):
            return str(item.pk)
        elif isinstance(item, Message):
            return str(item.pk)
        else:
            raise Http404


class AtomActivityFeed(RssActivityFeed):
    feed_type = Atom1Feed

    def subtitle(self, obj):
        return "Corsi della Scuola Galileiana di Studi Superiori"
