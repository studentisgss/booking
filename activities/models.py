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
        return "%s%s %s" % ("* " if not self.archived else "",
                            self.title, self.description)

    CLASS_CHOICES = [
        ("SN", "Scienze Naturali"),
        ("SM", "Scienze Morali"),
        ("SS", "Scienze Sociali"),
        ("A", "Altro")
    ]

    category = models.CharField(max_length=3, choices=CLASS_CHOICES, verbose_name=_("classe"))
    title = models.CharField(max_length=80, verbose_name=_("titolo"))
    professor = models.CharField(max_length=50, verbose_name=_("professore"))
    description = models.TextField(blank=True, verbose_name=_("descrizione"))
    archived = models.BooleanField(default=False, verbose_name=_("archiviata"))
    creator = models.ForeignKey(
        User,
        related_name="activity_created",
        on_delete=models.CASCADE,
        verbose_name=_("creatore")
    )
