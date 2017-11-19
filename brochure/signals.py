from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from activities.models import Activity


@receiver(post_save, sender=Activity)
def deleteBrochurePDFCache(sender, instance, **kwargs):
    cache.delete(instance.category)
