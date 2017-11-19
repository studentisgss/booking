from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.core.cache import cache

from activities.models import Activity

@receiver(post_save, sender=Activity)
def deleteBrochurePDFCache(sender, **kwargs):
    cache.delete_many(['SN', 'SM', 'SS'])
