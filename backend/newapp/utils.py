from rest_framework import status
from .models import Policy as Access_policy

from django.http import HttpResponse,JsonResponse
from django.conf import settings

from rest_framework.viewsets import ModelViewSet
from rest_access_policy import AccessPolicy

def get_access_statments(access_policies):
    policies = []
    for access_policy in access_policies:
        actions=  access_policy.action.split(',')
        principal=access_policy.principal.split(',')
        conditions=access_policy.conditions
        if conditions:
            conditions=access_policy.conditions.split(',')
            policy = {
            'action':actions,
            'principal':principal,
            'effect': access_policy.effect,
            'condition':conditions
        }
        else:
            policy = {
                'action':actions,
                'principal':principal,
                'effect': access_policy.effect
            }
        policies.append(policy)
    return policies 


def get_principal_ids(access_policies):
        id_list = []
        for policy in access_policies:
            principals = policy["principal"]
            for principal in principals:
                if principal.startswith("id:"):
                    # Extract the ID from the principal
                    id_value = principal.split(":")[1]
                    id_list.append(int(id_value))
        return id_list