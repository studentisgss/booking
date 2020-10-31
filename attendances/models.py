from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from string import *
from events.models import Event


class GalileianAttendance(models.Model):
    """
    A Galileian record represent the attendance of a
    galileian in a lesson.
    It's referred to an event and a user.
    Have a chair number.
    """
    class Meta:
        verbose_name = _("presenza galileiano")
        verbose_name_plural = _("presenze galileiani")

    def __str__(self):
        return self.event.room.name + " @ " + self.chair + " : " + self.user.username

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_("lezione")
    )
    chair = models.CharField(max_length=10, verbose_name=_("Sedia"))
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("utente")
    )


class ForeignAttendance(models.Model):
    """
    A Foreign record represent the attendance of a
    foreign student in a lesson.
    It's referred to an event.
    Have a chair number, a first name, a last name, a email, a phone number, a matricola
    """
    class Meta:
        verbose_name = _("presenza esterno")
        verbose_name_plural = _("presenze esterni")

    def __str__(self):
        return self.event.room.name + " @ " + self.chair + " : (F) " + self.first_name + " " + self.last_name

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_("lezione")
    )
    chair = models.CharField(max_length=10, verbose_name=_("Sedia"))
    first_name = models.CharField(max_length=100, verbose_name=_("Nome"))
    last_name = models.CharField(max_length=100, verbose_name=_("Cognome"))
    cell_number = models.CharField(max_length=100, verbose_name=_("Cellulare"))
    matricola = models.CharField(max_length=100, verbose_name=_("Matricola"))
    email = models.CharField(max_length=100, verbose_name=_("EMail"))


class Details(models.Model):
    """
    Save the details of registered user.
    It's referred to an user.
    Have a phone number field and a matricola field.
    """
    class Meta:
        verbose_name = _("dettagli")
        verbose_name_plural = _("dettagli")
        permissions = [
            ('get_attendances_data', 'Può scaricare i dati sulle presenze')
        ]

    def __str__(self):
        return self.user.username + " (" + self.matricola + ")"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("utente"),
        primary_key=True
    )
    cell_number = models.CharField(max_length=100, verbose_name=_("Cellulare"))
    matricola = models.CharField(max_length=100, verbose_name=_("Matricola"))
