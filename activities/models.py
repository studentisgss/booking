from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Activity(models.Model):
    """
    Attivita' della scuola per cui vengono create prenotazioni,
    innanzitutto i corsi interni.
    Contengono informazioni pubbliche come nome del corso/attivita',
    poi eventualmente altre relatore/professore, descrizione, classe
    "status" contiene lo stato di approvazione [IGNORARE-EXTRA]
    Quelli contrassegnati da "important" saranno evidenziati del software.
    "creator" e' l'utente che ha creato il corso
    "manager" sara' l'utente responsabile [IGNORARE-EXTRA]
    ---
    Activities of the School for which bookings are created,
    in first place internal courses.
    They contain public information such as name of course/activity,
    then eventually others: lecturer/professor, description and class.
    "status" contains the state of acceptance [IGNORE-EXTRA]
    "important"-tagged activities will be highlighted by software.
    "creator" is the user that created the course.
    "manager" is the manager of the course.
    """
    class Meta:
        verbose_name_plural = "Activities"

    def __str__(self):
        return "%s%s %s" % ("* " if self.important else "",
                            self.category, self.title)

    title = models.CharField(max_length=80, unique_for_date="start")
    teacher = models.CharField(max_length=80, default="")
    classe = models.CharField(max_length=8)
    description = models.CharField(max_length=500)
    important = models.BooleanField(default=False)
    creator = models.ForeignKey(User, related_name="activity_created")
