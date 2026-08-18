from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cycle

from django.dispatch import Signal

cycle_added = Signal()
@receiver(cycle_added)
def handle_cycle_added(sender, **kwargs):
    cycle_data = kwargs.get('cycle_data')
    print("Cycle added:", cycle_data)
