from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class News(models.Model):
    """
    Messages that will be shown on the website and on monitor.
    """
    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")

    def __str__(self):
        return self.title

    title = models.CharField(max_length=100, unique_for_date="start", verbose_name=_("title"))
    content = models.CharField(max_length=512, verbose_name=_("content"))
    start = models.DateField(_("Start date"))
    end = models.DateField(_("End date"))
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("creator"))
