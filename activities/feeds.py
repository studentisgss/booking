from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from django.http import Http404
from events.models import Event
from activities.models import Activity
from base.utils import localnow
from booking.settings import TIME_ZONE


class RssActivityFeed(Feed):

    description_template = "activities/feed/description.html"

    def get_object(self, request, activity_id):
        try:
            return Activity.objects.get(pk=activity_id)
        except Activity.DoesNotExist:
            raise Http404

    def title(self, obj):
        return "Corsi Scuola Galileiana"

    def link(self, obj):
        return reverse("events:calendar")

    def description(self, obj):
        return "Corsi della Scuola Galileiana di Studi Superiori"

    def items(self, obj):
        return Event.objects.filter(activity=obj, start__date=localnow().date(), status=0)

    def item_title(self, item):
        return item.activity.get_full_title()

    # def item_description(self, item):
    #     return "%s, %s - %s" % (
    #         item.room.name,
    #         item.start.strftime("%d/%m/%Y %H:%M"),
    #         item.end.strftime("%H:%M")
    #     )

    def item_link(self, item):
        return reverse("activities:details", kwargs={"activity_id": item.activity_id})

    def item_guid(self, obj):
        return str(obj.pk)


class AtomActivityFeed(RssActivityFeed):
    feed_type = Atom1Feed

    def subtitle(self, obj):
        return "Corsi della Scuola Galileiana di Studi Superiori"
