from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Activity(models.Model):
    """
    Activities of the School for which bookings are created,
    in first place internal courses.
    They contain public information such as name of course/activity,
    then eventually others: lecturer/professor, description or class.
    "status" contains the state of acceptance [IGNORE-EXTRA].
    "archived"-tagged activities will be not highlighted by software.
    "creator" is the user that created the course.
    "manager" is the manager of the course.
    """
    class Meta:
        verbose_name = _("attività")
        verbose_name_plural = _("attività")

    def __str__(self):
        return "%s%s " % ("* " if not self.archived else "",
                          self.title)

    def get_full_title(self):
        t = ""
        if self.category != "A":
            t = "%s - " % (self.category)
        t += self.title
        if self.professor != "":
            t += " (%s)" % (self.professor)
        return t

    CLASSES_WITH_TRANSLATION = [
        ("SN", "Scienze Naturali", "Natural Sciences"),
        ("SM", "Scienze Morali", "Moral Sciences"),
        ("SS", "Scienze Sociali", "Social Sciences"),
        ("A", "Altro", "Other")
    ]

    CLASS_CHOICES = [(choice[0], choice[1])
                     for choice in CLASSES_WITH_TRANSLATION]

    DESCRIPTION_TEMPLATE = """affiliazione - [email@example.com](mailto:email@example.com)

## Motivations
Inserire qui il testo

## Targeted audience
Inserire qui il testo

## Prerequisites
Inserire qui il testo

## Syllabus
Inserire qui il testo

## Teacher's CV
Inserire qui il testo

## Textbook/bibliography
Inserire qui il testo
    """

    category = models.CharField(max_length=3, choices=CLASS_CHOICES,
                                verbose_name=_("classe"), default="A")
    title = models.CharField(max_length=80, verbose_name=_("titolo"))
    professor = models.CharField(max_length=50, blank=True,
                                 verbose_name=_("professore"))
    description = models.TextField(blank=True, verbose_name=_("descrizione"),
                                   default=DESCRIPTION_TEMPLATE)
    archived = models.BooleanField(default=False, verbose_name=_("archiviata"))
    creator = models.ForeignKey(
        User,
        related_name="activity_created",
        on_delete=models.CASCADE,
        verbose_name=_("creatore")
    )
