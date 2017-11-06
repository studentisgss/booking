from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _


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
    A table with the opening times.
    To every room, every day is associated the opening timens during wich is allowed to book the room.
    """
    class Meta:
        verbose_name = _("orari dell'aula")
        verbose_name_plural = _("orari delle aule")

    def __str__(self):
        return "Aula%d Giorno%d" % (self.room_id, self.day_id)

    DAYS_OF_WEEK = [
        (0, 'Lunedì'),
        (1, 'Martedì'),
        (2, 'Mercoledì'),
        (3, 'Giovedì'),
        (4, 'Venerdì'),
        (5, 'Sabato'),
        (6, 'Domenica'),
     ]

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name=_("aula"))
    day = models.CharField(
        max_length=1,
        choices=DAYS_OF_WEEK,
        verbose_name="giorno")
    opening_time = models.TimeField(
        verbose_name="orario di apertura")
    closing_time = models.DateField(
        verbose_name="orario di chiusura")
