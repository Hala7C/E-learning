from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import BaseProfile,StudentProfile
from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Permission,Group

User=get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name="Student")
        instance.groups.add(group)
        StudentProfile.objects.create(user=instance, name=instance.get_full_name)
        


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied("Too many failed login attempts")