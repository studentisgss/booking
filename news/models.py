from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class News(models.Model):
    """
    Avvisi che verranno visualizzati sul sito e sul monitor
    ---
    Messages that will be shown on the website and on monitor
    """
    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return self.title

    title = models.CharField(max_length=100, unique_for_date="start")
    content = models.CharField(max_length=512)
    start = models.DateTimeField("Start Date")
    end = models.DateTimeField("End Date")
    active = models.BooleanField(default=False)
    creator = models.ForeignKey(User)
