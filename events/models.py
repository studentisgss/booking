from django.db import models
from django.contrib.auth.models import User
from rooms.models import Place
from activities.models import Activity

# Create your models here.


class Event(models.Model):
    """
    Events associated to an "activity" for which a "place" is booked,
    for example lessons of internal courses.
    "place" and "activity" are activity and place associated to the booking.
    "start" and "end" are time of the beginning and ending
    [WN: we require that beginning and ending are the same date]
    "status" is the state of acceptance of the booking.
    "creator" is the user that created/required the booking.
    """
    def __str__(self):
        return "%d %s" % (self.activity_id, self.start)

    """
    STATUS_CHOICES contains possible values for states of events and
    activities. Events and activities are automatically approved if the user that
    has created them has enough privilege level, 
    otherwise they shound approved/denied manually.
    """
    STATUS_CHOICES = [
        (0, "Approved"),
        (1, "Waiting"),
        (2, "Rejected"),
    ]
    place = models.ForeignKey(Place)
    activity = models.ForeignKey(Activity)
    start = models.DateTimeField("Start time")
    end = models.DateTimeField("End time")
    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    creator = models.ForeignKey(User, related_name="event_created")
