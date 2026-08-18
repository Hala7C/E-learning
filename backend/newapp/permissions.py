from rest_framework.permissions import BasePermission
from rest_access_policy import AccessPolicy
from newapp.models import *
from newapp.utils import *
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import NotFound
from eLearning import settings
from django.shortcuts import get_list_or_404, get_object_or_404
class NotificationPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='notification').get()
        access_policies = Policy.objects.filter(statmant=statment)
        policies=get_access_statments(access_policies)
        statements=policies
    except Statment.DoesNotExist as e:
        if  settings.IS_DATA_LOADED == False :
            pass
        else :
            raise NotFound(f"The requested resource was not found. {e}")
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        message = view.get_object()
        user_group=f'user_{request.user.id}'
        group_name=message.group_name
        return group_name == user_group


class PermissionPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='Policy').get()
        access_policies = Policy.objects.filter(statmant=statment)
        policies=get_access_statments(access_policies)
        statements=policies
    except Statment.DoesNotExist as e:
        if  settings.IS_DATA_LOADED == False :
            pass
        else :
            raise NotFound(f"The requested resource was not found. {e}")
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        modelName = request.data.get('model')
        pk = request.data.get('object_id')
        content_type = ContentType.objects.get(model=modelName)
        instance = get_object_or_404(content_type.model_class(), pk=pk)
        return instance.owner == request.user
        # Check if instance.user is equal to request.user
        # return instance.user == request.user
        # return group_name == user_group

