from django.utils import timezone
from datetime import datetime


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


def collect_urls(patterns):
    all_urls = []
    for entry in patterns:
        url = entry.regex.pattern
        if hasattr(entry, "url_patterns"):
            for url_suffix in collect_urls(entry.url_patterns):
                all_urls.append([url] + url_suffix)
        else:
            all_urls.append([url])
    return all_urls
