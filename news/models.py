from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class News(models.Model):
    """
    Messages that will be shown on the website and on monitor.
    """
    class Meta:
        verbose_name = _("avviso")
        verbose_name_plural = _("avvisi")

    def __str__(self):
        return self.title

    title = models.CharField(max_length=100, unique_for_date="start", verbose_name=_("titolo"))
    content = models.CharField(max_length=512, verbose_name=_("contenuto"))
    start = models.DateField(_("data di inizio"))
    end = models.DateField(_("data di fine"))
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("creatore"))

    def clean(self):
        if self.start is None:
            raise ValidationError(_("La data d'inizio non è corretta"))

        if self.end is None:
            raise ValidationError(_("La data di fine non è corretta"))

        # 1. Check that the start date is before or equal to the end date
        if self.start > self.end:
            raise ValidationError(_("La data di inizio deve precedere quella di fine"))
