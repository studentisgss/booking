from django.conf import settings
from base.models import CLASS_CHOICES
from events.models import Event


def demo(request):
    return {'DEMO': settings.DEMO}


def waiting_events_counter(request):
    """
    The variable name is "waiting_events_count"
    Return the number of events that the user can approve or refuse. The user has to have the
    correct permissions which include that to manage the category of the relative activity.
    If the user is not logged in or does not have the required permissions it returns None
    """
    if (request.user.is_authenticated and
            request.user.has_perms(("events.change_event", "activities.change_activity"))):
        # Get the managed category
        managed_category = [c[0] for c in CLASS_CHOICES
                            if request.user.has_perm("activities.change_" + c[0])]
        # Filter the events and count them
        event_count = Event.objects.filter(
            status=Event.WAITING,
            activity__category__in=managed_category
        ).filter(
            room__roompermission__group__in=request.user.groups.all(),
            room__roompermission__permission=30
        ).distinct().count()
        return {"waiting_events_count": event_count}
    else:
        return {"waiting_events_count": None}
