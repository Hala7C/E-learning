
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.auth import get_user_model
from .models import Role
from rest_framework import serializers
import sys
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission,Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Avg
from rating.models import Rating
from .models import CustomUser
import django.contrib.auth.password_validation as validators
from trainer.serializers import TrainerProfileSerializers,CourseSerializer
from payments.serializers import AccountDetailSerializer,PayoutSerializer,CourseSubscrubtionSerializer
User=get_user_model()


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
            model = Role
            fields=['name']

            
class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    password = serializers.CharField(required=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        model=User
        fields=['id','email','first_name','last_name','password','is_active', 'logged_in', 'otp_base32']

    def validate(self, data):
        user = User(**data)
        password = data.get('password')
        errors = dict() 
        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super(CustomUser, self).validate(data)

    def to_representation(self,instance):
        representation=super().to_representation(instance)
        if User.objects.filter(groups__name = "Trainer"):
        #   rate_value =representation['rate_value']
          content_type = ContentType.objects.get_for_model(User)
          average_rate = Rating.objects.filter(content_type=content_type, object_id=instance.id).aggregate(Avg('rate_value'))['rate_value__avg']
          representation['average_rate']=average_rate
          return representation    
        

    
    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        
        
        

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'content_type', 'codename')
        
        
class GroupPermissionSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    permission_ids = serializers.ListField(child=serializers.IntegerField())
    
    
class UserGroupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    group_ids = serializers.ListField(child=serializers.IntegerField())
    





class TrainerSerializer(serializers.HyperlinkedModelSerializer):
    profile=TrainerProfileSerializers(read_only=True,source='teacher_profile')
    courses=CourseSerializer(many=True,required=False,read_only=True)
    account=AccountDetailSerializer(read_only=True,source='acconutDetail')
    payouts=PayoutSerializer(many=True,read_only=True,source='user')
    class Meta(BaseUserRegistrationSerializer.Meta):
        model=User
        fields=['id','email','first_name','last_name','is_active', 'logged_in','profile','courses','account','payouts']


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    profile=TrainerProfileSerializers(read_only=True,source='student_profile')
    courses=CourseSubscrubtionSerializer(many=True,required=False,read_only=True,source='course_subscriptions')
    class Meta:
        model=User
        fields=['id','email','first_name','last_name','is_active', 'logged_in','profile','courses']
