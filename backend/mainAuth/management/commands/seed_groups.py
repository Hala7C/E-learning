from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

# These three names are load-bearing, not arbitrary:
#   "Student" - mainAuth/signals.py assigns every newly created user to
#               this group unconditionally (Group.objects.get(name="Student")),
#               so user registration is broken until this group exists.
#   "Trainer" - checked by IsTrainerUser (payments/permissions.py) and
#               referenced by the "group:Trainer" principal in seeded
#               course/cycle policies.
#   "Admin"   - checked by IsAdminUser (mainAuth/permissions.py) and by
#               the "group:Admin" principal in the Category policy.
GROUP_NAMES = ["Student", "Trainer", "Admin"]


class Command(BaseCommand):
    help = "Seed the Student/Trainer/Admin groups the app assumes exist."

    def handle(self, *args, **options):
        for name in GROUP_NAMES:
            _, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "already existed"
            self.stdout.write(self.style.SUCCESS(f"Group '{name}': {status}"))
