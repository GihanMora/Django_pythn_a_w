from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project


@receiver(post_save, sender=Project)
def queue_project_for_processing(sender, instance, created, **kwargs):
    # Push to queue here.
    print()
