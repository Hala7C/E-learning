from rest_framework.permissions import BasePermission
from rest_access_policy import AccessPolicy
from newapp.models import *
from newapp.utils import *
from django.contrib.contenttypes.models import ContentType
from payments.models import AcconutDetail
from rest_framework.exceptions import NotFound
from eLearning import settings
class IsTrainerUser(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated:
            return user.groups.filter(name='Trainer').exists()
        return False

class CourseSubscrubtionPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='CourseSubscrubtion').get()
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
        courseSubscribe = view.get_object()
        user=request.user
        trainer=courseSubscribe.course.trainer
        return trainer == user


class TransactionPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='Transaction').get()
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





class AccountDetailPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='AccountDetail').get()
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
    def account_detail_exist(self, request, view, action) -> bool:
        user=request.user
        Account_detail=AcconutDetail.objects.filter(trainer=user).exists()
        self.message = "You don't have account yet !! "
        return Account_detail


class EnrollmentPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='Enrollment').get()
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


class StripeAuthorizePolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='StripeAuthorize').get()
        access_policies = Policy.objects.filter(statmant=statment)
        policies=get_access_statments(access_policies)
        statements=policies
    except Statment.DoesNotExist as e:
        if  settings.IS_DATA_LOADED == False :
            pass
        else :
            raise NotFound(f"The requested resource was not found. {e}")


class PayoutPolicy(AccessPolicy):
    try:
        statment=Statment.objects.filter(view_name='Payout').get()
        access_policies = Policy.objects.filter(statmant=statment)
        policies=get_access_statments(access_policies)
        statements=policies
    except Statment.DoesNotExist as e:
        if  settings.IS_DATA_LOADED == False :
            pass
        else :
            raise NotFound(f"The requested resource was not found. {e}")
    def is_connect_account_exist(self, request, view, action) -> bool:
        user=request.user
        Account_detail=AcconutDetail.objects.get(trainer=user)
        connect=Account_detail.connect_account
        if connect is not None:
            return True
        else:
            self.message = "You don't have account yet !! add connect account to user profile so you can tansfer money . "
            return False
        
