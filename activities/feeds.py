from django.contrib.syndication.views import Feed
from django.views import View
from django.http import HttpResponse
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from django.http import Http404
from events.models import Event
from news.models import News, Message
from activities.models import Activity
from base.utils import localnow
from booking.settings import TIME_ZONE
import hashlib
import icalendar
from datetime import timedelta


class RssActivityFeed(Feed):

    description_template = "activities/feed/description.html"

    def get_object(self, request, activity_id):
        try:
            activity = Activity.objects.get(pk=activity_id)
            if activity.archived:
                raise Http404
            else:
                return activity
        except (Activity.DoesNotExist, OverflowError):
            raise Http404

    def title(self, obj):
        return "Attività Scuola Galileiana"

    def link(self, obj):
        return reverse("events:calendar")

    def description(self, obj):
        return "Attività della Scuola Galileiana di Studi Superiori"

    def items(self, obj):
        ret = list(Event.objects.filter(activity=obj, start__date=localnow().date(), status=0)) + \
            list(News.objects.filter(start__lte=localnow().date(), end__gte=localnow().date())) + \
            list(Message.objects.filter(activity=obj))
        if obj.event_set.all().filter(
            status=0,
            start__date__gte=localnow().date()
        ).exists():
            ret = [obj] + ret
        return ret

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(kwargs["item"], Event):
            context["type"] = "event"
        elif isinstance(kwargs["item"], News):
            context["type"] = "news"
        elif isinstance(kwargs["item"], Message):
            context["type"] = "message"
        elif isinstance(kwargs["item"], Activity):
            context["type"] = "activity"
            context["events"] = kwargs["item"].event_set.all().filter(
                status=0,
                start__date__gte=localnow().date()
            ).order_by("start")
        else:
            raise Http404
        return context

    def item_title(self, item):
        if isinstance(item, Event):
            return item.activity.title
        elif isinstance(item, News):
            return item.title
        elif isinstance(item, Message):
            return item.activity.title + ": " + item.title
        elif isinstance(item, Activity):
            return "Calendario di " + item.title
        else:
            raise Http404

    def item_link(self, item):
        if isinstance(item, Event):
            return reverse("activities:details", kwargs={"activity_id": item.activity_id})
        elif isinstance(item, News):
            return reverse("news:news")
        elif isinstance(item, Message):
            return "mailto:%s" % item.creator.email
        elif isinstance(item, Activity):
            return reverse("activities:details", kwargs={"activity_id": item.id})
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
        elif isinstance(item, Activity):
            # Use the guid to check if there is chenges in the events
            guid = "%d" % item.pk
            for e in item.event_set.all().filter(status=0).order_by("id"):
                guid += str(e.pk) + str(e.room.pk) + e.start.strftime("%Y%m%d%H%M")
                guid += e.end.strftime("%Y%m%d%H%M")
            sha1 = hashlib.sha1(guid.encode())
            return sha1.hexdigest()
        else:
            raise Http404

    def item_guid_is_permalink(self, item):
        return False


class AtomActivityFeed(RssActivityFeed):
    feed_type = Atom1Feed

    def subtitle(self, obj):
        return "Corsi della Scuola Galileiana di Studi Superiori"


class ICalActivityFeed(View):

    def get(self, request, activity_id):
        # Get the activity
        try:
            activity = Activity.objects.get(pk=activity_id)
        except (Activity.DoesNotExist, OverflowError):
            raise Http404
        # Do not process archived activity
        if (activity.archived):
            raise Http404
        # Initializa the calendar
        cal = icalendar.Calendar()
        cal.add("PRODID", "-//Scuola Galileiana di Studi Superiori di Padova//Booking//IT")
        cal.add("VERSION", "2.0")
        cal.add("METHOD", "PUBLISH")
        cal.add("CALSCALE", "GREGORIAN")
        cal.add("NAME", activity.get_full_title())
        cal.add("X-WR-CALNAME", activity.get_full_title())
        duration = icalendar.vDuration(timedelta(hours=8))
        cal.add("REFRESH-INTERVAL", duration)
        cal.add("X-PUBLISHED-TTL", duration)
        # Add the confirmed event
        url = request.build_absolute_uri(
            reverse("activities:details", kwargs={"activity_id": activity_id})
        )
        for e in Event.objects.filter(activity=activity, status=0).order_by("start"):
            event = icalendar.Event()
            event.add("dtstamp", localnow())
            event.add("uid", str(e.pk) + "@booking.scuolagalileiana.unipd.it")
            event.add("dtstart", e.start)
            event.add("dtend", e.end)
            event.add("summary", activity.title)
            event.add("location", e.room.get_full_name())
            event.add("status", "CONFIRMED")
            event.add("url", url)
            cal.add_component(event)
        return HttpResponse(cal.to_ical(), content_type="text/calendar")
