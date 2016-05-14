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
        verbose_name = _('evento')
        verbose_name_plural = _('eventi')

    def __str__(self):
        return _(
            "[%(day)s, %(start)s - %(end)s] %(room)s: %(activity)s"
        ) % {
            "activity": self.activity.title,
            "room": self.room.name,
            "day": self.start.strftime("%m/%d/%Y"),
            "start": self.start.strftime("%H:%M"),
            "end": self.end.strftime("%H:%M"),
        }

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
        (APPROVED, _("Approvato")),
        (WAITING, _("In attesa")),
        (REJECTED, _("Rifiutato")),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_("aula"))
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name=_("attività"))
    start = models.DateTimeField(_("ora di inizio"))
    end = models.DateTimeField(_("ora di fine"))
    status = models.SmallIntegerField(choices=STATUS_CHOICES, verbose_name=_("stato"))
    creator = models.ForeignKey(
        User,
        related_name="event_created",
        on_delete=models.CASCADE,
        verbose_name=_("creatore")
    )

    def clean(self):
        # 1. Check that the start time is before the end time
        if self.start >= self.end:
            raise ValidationError(_("L'ora di inizio deve precedere quella di fine"))

        # 2. Check that the start and end time are in the same day
        day_start = self.start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        if self.end > day_end:
            raise ValidationError(_(
                "L'ora di inizio e quella di fine devono essere nello stesso giorno"
            ))

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
                    _("Non possono esserci due eventi non rifiutati sovrapposti per la stessa aula")
                )
