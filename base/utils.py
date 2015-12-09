# Common utilities


def localnow():
    """
    Return a datetime object representing the time in the local timezone
    """
    return timezone.localtime(timezone.now(), timezone.get_default_timezone())
