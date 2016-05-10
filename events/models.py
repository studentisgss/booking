from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import timedelta

from rooms.models import Room
from activities.models import Activity


class Event(models.Model):
    """
    Events associated to an "activity" for which a "room" is booked,
    for example lessons of internal courses.
    "room" and "activity" are activity and room associated to the booking.
    "start" and "end" are time of the beginning and ending
    [WN: we require that beginning and ending are the same date]
    "status" is the state of acceptance of the booking.
    "creator" is the user that created/required the booking.
    """
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return "%d %s" % (self.activity_id, self.start)

    """
    STATUS_CHOICES contains possible values for states of events and
    activities. Events and activities are automatically approved if
    the user that has created them has enough privilege level,
    otherwise they shound approved/denied manually.
    """
    APPROVED = 0
    WAITING = 1
    REJECTED = 2
    STATUS_CHOICES = [
        (APPROVED, _("Approved")),
        (WAITING, _("Waiting")),
        (REJECTED, _("Rejected")),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_("room"))
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name=_("activity"))
    start = models.DateTimeField(_("Start time"))
    end = models.DateTimeField(_("End time"))
    status = models.SmallIntegerField(choices=STATUS_CHOICES, verbose_name=_("status"))
    creator = models.ForeignKey(
        User,
        related_name="event_created",
        on_delete=models.CASCADE,
        verbose_name=_("creator")
    )

    def clean(self):
        # 1. Check that the start time is before the end time
        if self.start >= self.end:
            raise ValidationError(_("Start time must precede end time"))

        # 2. Check that the start and end time are in the same day
        day_start = self.start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        if self.end > day_end:
            raise ValidationError(_("Start time and end time must be in the same day"))

        # 3. If this event is not rejected, check that it does not overlap with all
        # the other not-rejected events booked for the same room
        if self.status != Event.REJECTED:
            is_overlapping = Event.objects.filter(
                ~Q(status=Event.REJECTED),
                room_id=self.room.pk
            ).filter(
                # Keep only overlapping events
                Q(start__lt=self.end),
                Q(end__gt=self.start)
            ).exists()
            if is_overlapping:
                raise ValidationError(
                    _("There cannot be two overlapping, not rejected events for the same room")
                )
