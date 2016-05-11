from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


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
