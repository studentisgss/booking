from django.db import models
from django.contrib.auth.models import User

# Create your models here.


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
        verbose_name_plural = "Activities"

    def __str__(self):
        return "%s%s %s" % ("* " if not self.archived else "",
                            self.title, self.description)

    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    archived = models.BooleanField(default=False)
    creator = models.ForeignKey(User, related_name="activity_created", on_delete=models.CASCADE)
