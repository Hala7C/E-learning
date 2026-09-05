from django.core.management.base import BaseCommand
from django.db import transaction

from newapp.models import Statment, Policy

# Keyed by the exact `view_name` each AccessPolicy subclass looks up
# (see trainer/permissions.py, payments/permissions.py, newapp/permissions.py).
# `action`/`principal`/`conditions` are comma-separated strings, matching
# how get_access_statments() (newapp/utils.py) splits them - no spaces
# around the commas.
#
# principal values rest_access_policy understands: "*" (anyone, including
# anonymous), "authenticated", "anonymous", "admin", "staff",
# "group:<name>", "id:<pk>".
#
# Only the four statements the trainer course/cycle screens actually need
# are filled in below. The rest of the codebase's view_names are listed
# at the bottom as a checklist - add them here the same way as you build
# out those areas, rather than guessing their business rules now.
POLICY_SEED = {
    "Course": [
        {"action": "list,retrieve,getTrainerCourse", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "group:Trainer", "effect": "allow"},
        {
            "action": "update,partial_update,destroy,give_obj_perm,delete_translation",
            "principal": "*",
            "effect": "allow",
            "conditions": "is_owner",
        },
    ],
    "Category": [
        {"action": "list,retrieve", "principal": "*", "effect": "allow"},
        {"action": "create,update,destroy,delete_translation", "principal": "group:Admin", "effect": "allow"},
    ],
    "Cycle": [
        {"action": "list,retrieve", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "group:Trainer", "effect": "allow"},
        {"action": "update,partial_update,destroy", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "LiveSessionMainData": [
        {"action": "list,retrieve", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "group:Trainer", "effect": "allow"},
        {"action": "update,partial_update,destroy", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "LiveSessionDetails": [
        {"action": "list,retrieve", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "group:Trainer", "effect": "allow"},
        {"action": "update,partial_update,destroy", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "VedioSection": [
        {"action": "list,retrieve", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "group:Trainer", "effect": "allow"},
        {"action": "update,partial_update,destroy", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "DraftProfile": [
        {"action": "list,me,retrieve", "principal": "*", "effect": "allow  "},
        {"action": "create", "principal": "group:Student", "effect": "allow"},
        {"action": "update,partial_update,destroy", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "PendingProfile": [
        {"action": "list,me,retrieve", "principal": "*", "effect": "allow  "},
        {"action": "create", "principal": "group:Student", "effect": "allow"},
        {"action": "update,partial_update,destroy", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "SubmitProfile": [
        {"action": "update,partial_update", "principal": "*", "effect": "allow", "conditions": "is_owner"},
    ],
    "Skill": [
        {"action": "list,retrieve,me", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "*", "effect": "allow"},  
        {"action": "update,destroy", "principal": "*", "effect": "allow"},
        
    ],
    "Education": [
        {"action": "list,retrieve,me", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "*", "effect": "allow"},  
        {"action": "update,destroy", "principal": "*", "effect": "allow"},
    ],
    "Employment": [
        {"action": "list,retrieve,me", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "*", "effect": "allow"},  
        {"action": "update,destroy", "principal": "*", "effect": "allow"},
    ],
    "Achievement": [
        {"action": "list,retrieve,me", "principal": "*", "effect": "allow"},
        {"action": "create", "principal": "*", "effect": "allow"},  
        {"action": "update,destroy", "principal": "*", "effect": "allow"},
    ],
}

# Still need rules before their endpoints will do anything but deny:
#   newapp: "notification", "Policy"
#   payments: "CourseSubscrubtion", "Transaction", "AccountDetail",
#             "Enrollment", "StripeAuthorize", "Payout"
#   trainer: "PendingProfile", "SubmitProfile"


class Command(BaseCommand):
    help = "Seed Statment/Policy rows for the rest_access_policy AccessPolicy subclasses."

    @transaction.atomic
    def handle(self, *args, **options):
        for view_name, rules in POLICY_SEED.items():
            statement, _ = Statment.objects.get_or_create(view_name=view_name)
            # Replace rather than get_or_create per-rule, so editing a
            # rule above and re-running this command doesn't leave old,
            # stale rows sitting alongside the new ones.
            Policy.objects.filter(statmant=statement).delete()
            for rule in rules:
                Policy.objects.create(
                    statmant=statement,
                    action=rule["action"],
                    principal=rule["principal"],
                    effect=rule["effect"],
                    conditions=rule.get("conditions"),
                )
            self.stdout.write(self.style.SUCCESS(f"Seeded '{view_name}' ({len(rules)} rule(s))"))
