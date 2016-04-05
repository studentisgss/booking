from django.utils import timezone
from datetime import datetime

# Common utilities


def localnow():
    """
    Return a datetime object representing the time in the local timezone
    """
    return timezone.localtime(timezone.now(), timezone.get_default_timezone())


def default_datetime(*args, **kwargs):
    if 'tzinfo' not in kwargs:
        return datetime(*args, tzinfo=timezone.get_default_timezone(), **kwargs)
    else:
        return datetime(*args, **kwargs)
