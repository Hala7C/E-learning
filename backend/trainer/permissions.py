from rest_framework.permissions import BasePermission
from rest_access_policy import AccessPolicy
from newapp.models import *
from newapp.utils import *
from django.contrib.contenttypes.models import ContentType
from eLearning import settings
from rest_framework.exceptions import NotFound
from trainer.models import LiveSessionMainDataSection
class IsTrainerUser(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated:
            roles=user.roles.all()
            role_values = [role.name for role in roles]
            for role_value in role_values:
                if role_value == 'Trainer':
                    return True
        return False





    
class CoursePolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='Course')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        print("CoursePolicy statements:", get_access_statments(access_policies))
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        # check polomorphic
        course = view.get_object()
        content_type = ContentType.objects.get_for_model(course)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=course.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        course = view.get_object()
        return request.user == course.trainer
    def is_trainer_profile_approved(self, request, view, action) -> bool:
        user=request.user
        profile=user.teacherprofile
        return profile.status=="accepted"

    



class CategoryPolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='Category')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists

class VedioSectionPolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='VedioSection')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        video = view.get_object()
        return request.user == video.course.trainer

class LiveSessionMainDataPolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='LiveSessionMainData')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        liveSessionMainData = view.get_object()
        return request.user == liveSessionMainData.course.trainer



class LiveSessionDetailsPolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='LiveSessionDetails')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        policies=get_access_statments(access_policies)
        statements=policies
        return statements
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        liveSessionDetails = view.get_object()
        return request.user == liveSessionDetails.cycle.course.trainer

class CyclePolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='Cycle')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        cycle = view.get_object()
        return request.user == cycle.course.trainer


class CycleAccessPolicy(AccessPolicy):
    my_variable = None
    statements = [
        {
            "action": ["list","retrieve"],
            "principal": ["*"],
            "effect": "allow",
        },
        {
            "action": ["create"],
            "principal": ["*"],
            "effect": "allow",
            "condition":["is_live_sessions_created"]
        },
        {
            "action": ["update"],
            "principal": ["*"],
            "effect": "allow",
            "condition":["is_owner"]
        },
        {
            "action": ["destroy"],
            "principal": ["*"],
            "effect": "allow",
            "condition":["is_owner"]
        },
        {
            "action": ["getTrainerCourse"],
            "principal": ["*"],
            "effect": "allow",
        },
        {
            "action": ["give_obj_perm"],
            "principal": ["group:Trainer"],
            "effect": "allow",
        },
        {
            "action": ["delete_translation"],
            "principal": ["group:Trainer"],
            "effect": "allow",
        },
        

    ]

    @classmethod
    def set_variable(cls, value):
        cls.my_variable = value
    def is_owner(self, request, view, action) -> bool:
        course = view.get_object()
        return request.user == course.trainer
    def is_live_sessions_created(self, request, view, action) -> bool:
        cycle = self.my_variable
        if cycle:
            res=LiveSessionMainDataSection.objects.filter(course=cycle.course).count()
            if cycle.livesessiondetails.count() <= res: 
                return True
            return False
        return True
    


class DraftProfilePolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='DraftProfile')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)

    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        teacherProfile = view.get_object()
        return request.user == teacherProfile.user



class PendingProfilePolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='PendingProfile')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists




class SubmitProfilePolicy(AccessPolicy):
    @property
    def statements(self):
        try:
            statment = Statment.objects.get(view_name='SubmitProfile')
        except Statment.DoesNotExist:
            if settings.IS_DATA_LOADED:
                raise NotFound("The requested resource was not found.")
            return []
        access_policies = Policy.objects.filter(statmant=statment)
        return get_access_statments(access_policies)
    def is_assistant(self, request, view, action) -> bool:
        message = view.get_object()
        content_type = ContentType.objects.get_for_model(message)
        object_perm = ObjectPerm.objects.filter(content_type=content_type, object_id=message.id).first()
        user=request.user
        user_exists = ObjectPerm.objects.filter(users=user).exists()
        return user_exists
    def is_owner(self, request, view, action) -> bool:
        teacherProfile = view.get_object()
        return request.user == teacherProfile.user
