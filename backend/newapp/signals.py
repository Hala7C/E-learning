from django.dispatch import receiver
from .models import Notification
from django.dispatch import Signal

# Define a custom signal
notification_signal = Signal()



@receiver(notification_signal)
def handle_notification(sender, message, group_name, **kwargs):
    Notification.objects.create(message=message,group_name=group_name)
    print("Task completed with result ")