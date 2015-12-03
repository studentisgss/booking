from django.db import models
from django.contrib.auth.models import User
from rooms.models import Place
from activities.models import Activity

# Create your models here.

"""
STATUS_FLAGS contiene i possibili valori per gli stati di eventi e attivita'
Eventi e attivita' sono approvati automaticamente se creati da un utente con
sufficienti privilegi, altrimenti devono essere approvati o rifiutati
---
STATUS_FLAGS contains possible values for states of events and activities.
Events and activities are automatically approved if a user has enough
privilege level, otherwise they shound approved/denied manually.
"""
STATUS_FLAGS = [
    (0, "Approved"),
    (1, "Waiting"),
    (2, "Rejected"),
]


class Event(models.Model):
    """
    Eventi associati a una "attività" per cui viene prenotato un "luogo", ad
    esempio le lezioni dei corsi interni
    "place" e "activity" sono le attività
    e il luogo associati alle prenotazioni
    "start" e "end" sono gli orari di inizio e fine
    [NB: richiediamo che siano nella stessa data]
    "status" è lo stato di approvazione della prenotazione
    "creator" è l'utente che ha creato/richiesto la prenotazione
    ---
    Events associated to an "activity" for which a "place" is booked,
    for example lessons of internal courses.
    "place" and "activity" are activity and place associated to the booking.
    "start" and "end" are time of the beginning and ending
    [NB: we require that beginning and ending are the same date]
    "status" is the state of acceptance of the booking.
    "creator" is the user that created/required the booking.
    """
    def __str__(self):
        return "%d %s" % (self.activity_id, self.start)
    place = models.ForeignKey(Place)
    activity = models.ForeignKey(Activity)
    start = models.DateTimeField("Start Time")
    end = models.DateTimeField("End Time")
    status = models.SmallIntegerField(choices=STATUS_FLAGS)
    creator = models.ForeignKey(User, related_name="event_created")
