from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import timedelta

from rooms.models import Room
from rooms.models import RoomRule
from activities.models import Activity


class Event(models.Model):
    """
    Events associated to an "activity" for which a "room" is booked,
    for example lessons of internal courses.
    "room" and "activity" are activity and room associated to the booking.
    "online" is true if the lesson is online.
    Either "online" is true or "room" is not null.
    "start" and "end" are time of the beginning and ending
    "exam" is a flag to tell apart lectures from exams
    [WN: we require that beginning and ending are the same date]
    "status" is the state of acceptance of the booking.
    "lastEditor" is the user that created/last changed the booking.
    """
    class Meta:
        verbose_name = _('evento')
        verbose_name_plural = _('eventi')

    def __str__(self):
        return _(
            "[%(day)s, %(start)s - %(end)s] %(room)s: %(activity)s"
        ) % {
            "activity": self.activity.title,
            "room": (_("Lezione online") if self.online else self.room),
            "day": timezone.localtime(self.start).strftime("%d/%m/%Y"),
            "start": timezone.localtime(self.start).strftime("%H:%M"),
            "end": timezone.localtime(self.end).strftime("%H:%M"),
        }

    """
    STATUS_CHOICES contains possible values for states of events and
    activities. Events and activities are automatically approved if
    the user that has created them excludes enough privilege level,
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
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_("aula"), null=True, blank=True)
    online = models.BooleanField(default=False, verbose_name=_("online"))
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name=_("attività"))
    start = models.DateTimeField(_("ora di inizio"))
    end = models.DateTimeField(_("ora di fine"))
    exam = models.BooleanField(default=False, verbose_name=_("esame"))
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                      default=APPROVED, verbose_name=_("stato"))
    lastEditor = models.ForeignKey(
        User,
        related_name="event_modified",
        on_delete=models.CASCADE,
        verbose_name=_("Richiedente")
    )

    def get_full_title(self):
        return self.activity.get_full_title(self.exam)

    def clean(self):

        if self.start is None:
            raise ValidationError(_("La data/ora d'inizio non è corretta"))

        if self.end is None:
            raise ValidationError(_("La data/ora di fine non è corretta"))

        if self.room_id is None:
            if not self.online:
                raise ValidationError(_("L'aula è obbligatoria"))

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

        # 3. Check that the event is included in the opening times of the room
        # if they exists.
        try:
            roomRule = RoomRule.objects.get(day=self.start.weekday(), room=self.room)
            if self.start.timetz() < roomRule.opening_time or \
                    self.end.timetz() > roomRule.closing_time:
                raise ValidationError(_("L'aula risulta essere chiusa in quell'orario"))
        except ObjectDoesNotExist:
            pass

        # 4. If this event is not rejected and not online, check that it does not overlap with all
        # the other not-rejected events booked for the same room
        if self.status != Event.REJECTED and not self.online:
            overlapping_events = Event.objects.filter(
                ~Q(status=Event.REJECTED),
                room_id=self.room.pk
            ).filter(
                # Keep only overlapping events
                Q(start__lt=self.end),
                Q(end__gt=self.start)
            )
            # If the event is already in the database exclude it
            if self.pk is not None:
                overlapping_events = overlapping_events.filter(
                    ~Q(pk=self.pk)
                )
            is_overlapping = overlapping_events.exists()
            if is_overlapping:
                raise ValidationError(
                    _("Non possono esserci due eventi non rifiutati sovrapposti per la stessa aula")
                )
