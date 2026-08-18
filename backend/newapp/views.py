
from datetime import datetime

from django.contrib.auth.models import Permission, Group
from django.dispatch import Signal, receiver
from django.shortcuts import render

from mainAuth.models import CustomUser
from mainAuth.serializers import GroupSerializer, UserRegistrationSerializer
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Policy as Access_policy ,Statment,Action
from rest_framework.viewsets import ModelViewSet

from rest_access_policy import AccessPolicy

from .models import Policy as Access_policy, Notification
from .serializers import *
from .utils import *
from rest_framework.decorators import api_view,permission_classes
from django.dispatch import Signal, receiver
from django.contrib.auth.models import Permission,Group
from mainAuth.models import CustomUser
from rest_framework.decorators import action
from mainAuth.serializers import GroupSerializer,UserRegistrationSerializer
from django.shortcuts import render
from .models import Notification
from .permissions import *
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
def index1(request):
    user=request.user
    
    return render(request, 'index1.html',{'user': user})


class StatmentViewSet(ModelViewSet):
    queryset = Statment.objects.all()
    serializer_class = StatmentSerializer
    permission_classes=[PermissionPolicy]

class ActionViewSet(ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes=[PermissionPolicy]
    @action(methods=['get'],detail=True)
    def get_action_conditions(request,pk):
        action=Action.objects.get(id=pk)
        conditions = action.conditions_set.all()
        ser=ConditionsSerializer(conditions,many=True)
        return Response(ser.data,status.HTTP_200_OK)

class ConditionViewSet(ModelViewSet):
    queryset = Conditions.objects.all()
    serializer_class = ConditionsSerializer
    permission_classes=[PermissionPolicy]

class PolicyViewSet(ModelViewSet):
    queryset = Access_policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes=[PermissionPolicy]
    def list(self,request):
        accesspolicy=Access_policy.objects.all()
        serializer = PolicySerializer(accesspolicy,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    @action(methods=['get'],detail=False)
    def get_basic_principal(self, request, *args, **kwargs):
        data=["*","admin","staff","authenticated","anonymous"]
        return Response(data, status=201)
    @action(methods=['get'],detail=False)
    def get_user_principal(self, request, *args, **kwargs):
        users=CustomUser.objects.all()
        ser=UserRegistrationSerializer(users,many=True)
        return Response(ser.data, status=201)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, pk):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Access_policy.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
    @action(methods=['post'],detail=False)
    def give_obj_perm(self,request):
            
            modelName=request.data['model']
            pk=request.data['object_id']
            content_type = ContentType.objects.get(model=modelName)
            instance = get_object_or_404(content_type.model_class(), pk=pk)
            user=CustomUser.objects.get(pk=request.data['user_id'])
            p=ObjectPerm(content_object=instance)
            p.save()
            p.users.add(user)
            p.save()
            return Response({"message":"permission granted successfully"},status=status.HTTP_200_OK)

        



class NotificationViewSet(ModelViewSet):
    queryset=Notification.objects.all()
    serializer_class=NotificationSerializer
    permission_classes=[NotificationPolicy]
    def  get_queryset(self):
        queryset= super().get_queryset()
        is_read=self.request.query_params.get('is_read')
        if is_read :
            if is_read.lower()=='true':
                queryset=queryset.filter(is_read=True)
            elif is_read.lower()=='false':
                queryset=queryset.filter(is_read=False)
        return queryset

    def update(self, request, pk, format=None):
        try:
            instance = self.get_object()
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Notification.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)