from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from datetime import time
from string import *


class Building(models.Model):
    """
    A building is where the real rooms are located.
    It has a name, a creator and an address.
    The address is a normal string with spaces.
    """
    class Meta:
        verbose_name = _("edificio")
        verbose_name_plural = _("edifici")

    def __str__(self):
        return self.name

    name = models.CharField(max_length=50, unique=True, verbose_name=_("nome"))
    address = models.CharField(max_length=100, unique=True, verbose_name=_("indirizzo"))
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("creatore")
    )

    # Return a different strig for the address wich can be used in the url for the map.
    def get_address_for_url(self):
        s = self.address
        return s.replace(' ', '+')


class Room(models.Model):
    """
    Rooms where events will take place,
    firstable galileo rooms, aula magna and so on...
    Others rooms can be added later.
    "important"-tagged rooms will be highlighted by the software.
    Every room is part of a building.
    """
    class Meta:
        verbose_name = _("aula")
        verbose_name_plural = _("aule")
        permissions = (
            ("can_book_room", _("Può prenotare qualche aula")),
            ("can_change_important", _("Può cambiare importanza aula")),
        )
        unique_together = ("name", "building")

    def __str__(self):
        return "%s %s-%s" % ("*" if self.important else "", self.name, self.building.name)

    # Set the roompermission as default
    def create_roompermission(self):
        # delete existing roompermissions
        self.roompermission_set.all().delete()
        can_book_room_permission = Permission.objects.get(codename="can_book_room")
        if self.important:
            for group in Group.objects.filter(permissions=can_book_room_permission):
                permission = RoomPermission(room=self, group=group, permission=10)
                permission.save()
        else:
            for group in Group.objects.filter(permissions=can_book_room_permission):
                permission = RoomPermission(room=self, group=group, permission=30)
                permission.save()
            for group in Group.objects.exclude(permissions=can_book_room_permission):
                permission = RoomPermission(room=self, group=group, permission=10)
                permission.save()

    name = models.CharField(max_length=30, unique=False, verbose_name=_("nome"))
    description = models.CharField(max_length=100, blank=True, verbose_name=_("descrizione"))
    important = models.BooleanField(default=False, verbose_name=_("importante"))
    building = models.ForeignKey(
        Building,
        verbose_name=_("edificio")
    )
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

    # Return the name of the room made of the name of the room and the name of the building
    def get_full_name(self):
        return "%s - %s" % (self.name, self.building.name)


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
        return "Aula %s, Gruppo %s" % (self.room, self.group)

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

    def clean(self):
        # Do not check if there is the room!

        if self.group_id is None:
            raise ValidationError(_("Il nome del gruppo è obbligatorio"))

        # Check that there are not two timetables for the same room the same day
        overlapping_roomPermissions = RoomPermission.objects.filter(
            room_id=self.room.pk,
            group_id=self.group.pk)
        # If the event is already in the database exclude it
        if self.pk is not None:
            overlapping_roomPermissions = overlapping_roomPermissions.exclude(
                id=self.pk)
        if overlapping_roomPermissions.exists():
            raise ValidationError(
                _("Non possono permessi per la stessa aula e lo stesso gruppo")
            )


class RoomRule(models.Model):
    """
    An object with the opening times.
    To every room, every day is associated the opening times
    during wich is allowed to book the room.
    """
    class Meta:
        verbose_name = _("orari dell'aula")
        verbose_name_plural = _("orari delle aule")

    def __str__(self):
        return "Aula %s, Giorno %s" % (self.room, self.day)

    DAYS_OF_WEEK = [
        (0, _("Lunedì")),
        (1, _("Martedì")),
        (2, _("Mercoledì")),
        (3, _("Giovedì")),
        (4, _("Venerdì")),
        (5, _("Sabato")),
        (6, _("Domenica"))
    ]

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name=_("aula"))
    day = models.SmallIntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name=_("giorno"))
    opening_time = models.TimeField(
        verbose_name=_("orario di apertura"))
    closing_time = models.TimeField(
        verbose_name=_("orario di chiusura"))

    def clean(self):
        # Do not check if there is the room!

        if self.day is None:
            raise ValidationError(_("Il giorno è obbligatorio"))

        if self.opening_time is None or self.closing_time is None:
            raise ValidationError(_("Orari di apertura e chiusura sono obbligatori"))

        # 1. Check that the opening time is before the closing time
        if self.opening_time > self.closing_time:
            raise ValidationError(_("L'ora di apertura deve precedere quella di chiusura"))

        # 2. Check that there are not two timetables for the same room the same day
        overlapping_roomRules = RoomRule.objects.filter(
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

    # return true if the room is closed for all the day
    def isClosedAllDay(self):
        return self.opening_time == self.closing_time
