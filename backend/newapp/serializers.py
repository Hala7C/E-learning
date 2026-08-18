from rest_framework import serializers
from .models import Conditions,Action,Statment,Policy as Access_policy,Notification
from django.urls import path, include
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from rest_framework import routers, serializers, viewsets
from .mixins import TranslatedSerializerMixin
from rest_access_policy import FieldAccessMixin
from rest_access_policy import AccessPolicy
from .utils import *


class PolicySerializer(serializers.HyperlinkedModelSerializer):
    statmant = serializers.PrimaryKeyRelatedField(queryset=Statment.objects.all())

    class Meta:
        model = Access_policy
        fields = ('id','action', 'principal', 'effect','conditions','statmant')
        
class StatmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Statment
        fields = ('id','view_name')
        

class ActionSerializer(serializers.HyperlinkedModelSerializer):
    statment = serializers.PrimaryKeyRelatedField(queryset=Statment.objects.all())
    class Meta:
        model = Action
        fields = ('id','name','statment')
        
class ConditionsSerializer(serializers.HyperlinkedModelSerializer):
    actions  = ActionSerializer(many=True)
    class Meta:
        model = Conditions
        fields = ('id','name','actions')
        


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Notification
        fields=['id','message','group_name','is_read']