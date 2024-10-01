from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from xauth.models import User


@receiver(pre_save, sender=User)
def set_username(sender, **kwargs):
    instance: User = kwargs.get("instance")
    instance.username = instance.matricule

    if not instance.is_superuser:
        instance.is_active = False
