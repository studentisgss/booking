from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import time


class Room(models.Model):
    """
    Rooms where events will take place,
    firstable galileo rooms, aula magna and so on...
    Others rooms can be added later.
    "important"-tagged rooms will be highlighted by the software.
    """
    class Meta:
        verbose_name = _("aula")
        verbose_name_plural = _("aule")
        permissions = (
            ("can_book_room", _("Può prenotare qualche aula")),
        )

    def __str__(self):
        return "%s %s" % ("*" if self.important else "", self.name)

    name = models.CharField(max_length=30, unique=True, verbose_name=_("nome"))
    description = models.CharField(max_length=100, verbose_name=_("descrizione"))
    important = models.BooleanField(default=False, verbose_name=_("importante"))
    creator = models.ForeignKey(
        User,
        related_name="room_created",
        on_delete=models.CASCADE,
        verbose_name=_("creatore")
    )

    def get_group_perm(self, group):
        try:
            return RoomPermission.objects.get(
                room=self,
                group=group
            ).permission
        except RoomPermission.DoesNotExist:
            return 0

    def show_request_to_group(self, group):
        return RoomPermission.objects.get(room=self, group=group).showrequest


class RoomPermission(models.Model):
    """
    Permissions for every room and every group.
    To every room and every group is associated a level of permissions
    and if requests of this room are highlighted/shown for users of the group.
    """
    class Meta:
        verbose_name = _("permesso sull'aula")
        verbose_name_plural = _("permessi sulle aule")

    def __str__(self):
        return "Aula%d & Gruppo%d" % (self.room_id, self.group_id)

    PERMISSION_CHOICES = [
        (10, _("Può richiedere")),
        (30, _("Può accettare")),
    ]
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name=_("aula"),
        related_query_name='')
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name=_("gruppo"))
    permission = models.SmallIntegerField(
        choices=PERMISSION_CHOICES,
        default=10,
        verbose_name=_("permesso"))


class RoomRules(models.Model):
    """
    An object with the opening times.
    To every room, every day is associated the opening times during wich is allowed to book the room.
    """
    class Meta:
        verbose_name = _("orari dell'aula")
        verbose_name_plural = _("orari delle aule")

    def __str__(self):
        return "Aula %s Giorno %s" % (self.room,self.day)

    DAYS_OF_WEEK = [
        (1, _("Lunedì")),
        (2, _("Martedì")),
        (3, _("Mercoledì")),
        (4, _("Giovedì")),
        (5, _("Venerdì")),
        (6, _("Sabato")),
        (0, _("Domenica"))
     ]

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name=_("aula"))
    day = models.SmallIntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name="giorno")
    opening_time = models.TimeField(
        verbose_name="orario di apertura")
    closing_time = models.TimeField(
        verbose_name="orario di chiusura")

    def clean(self):
        if self.room_id is None:
            raise ValidationError(_("L'aula è obbligatoria"))

        if self.day is None:
            raise ValidationError(_("Il giorno è obbligatorio"))

        if self.opening_time is None or self.closing_time is None:
            raise ValidationError(_("Orari di apertura e chiusura sono obbligatori"))

        # 1. Check that the opening time is before the closing time
        if self.opening_time >= self.closing_time:
            raise ValidationError(_("L'ora di apertura deve precedere quella di chiusura"))

        # 2. Check that there are not two timetables for the same room the same day
        overlapping_roomRules = RoomRules.objects.filter(
            room_id=self.room.pk,
            day=self.day)
        # If the event is already in the database exclude it
        if self.pk is not None:
            overlapping_roomRules = overlapping_roomRules.exclude(
                id=self.pk)
        is_overlapping = overlapping_roomRules.exists()
        if is_overlapping:
            raise ValidationError(
                _("Non possono esserci due orari per la stessa aula lo stesso giorno")
            )
