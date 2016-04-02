from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class News(models.Model):
    """
    Messages that will be shown on the website and on monitor.
    """
    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return self.title

    title = models.CharField(max_length=100, unique_for_date="start")
    content = models.CharField(max_length=512)
    start = models.DateTimeField("Start date")
    end = models.DateTimeField("End date")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
