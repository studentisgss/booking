# Common utilities


def localnow():
    """
    Returns the local time
    """
    return timezone.localtime(timezone.now(), get_default_timezone())
