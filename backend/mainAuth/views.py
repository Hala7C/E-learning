from rest_framework import status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer,GroupSerializer,GroupPermissionSerializer,UserGroupSerializer,PermissionSerializer,TrainerSerializer,StudentSerializer
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission,Group
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from .services import *
from rest_framework.permissions import AllowAny,IsAuthenticated
User=get_user_model()
import qrcode
import qrcode.image.svg
from django.http import HttpResponse
from rest_framework import views
from djoser import signals, utils
from djoser.conf import settings
from django.db.models import DateTimeField
from django.db.models import F, Sum
from django.db.models.functions import ExtractYear, ExtractMonth,ExtractDay
from datetime import datetime, timedelta
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken 
from .models import *
from django.utils import timezone
from django.http import JsonResponse
from payments.models import Transaction,LiveSessionEnrollment
from trainer.models import *
from django.db.models import Count
from django.db.models import Sum, Q
from datetime import datetime

def lockout(request):
    return Response({"status": "Locked out due to too many login failures"}, status=status.HTTP_403_FORBIDDEN)


class Set2FAView(APIView):
 """
 Get the image of the QR Code

 """
 permission_classes=[IsAuthenticated]

 def post(self, request):
  user=request.user
  if user == None:
   return Response({"status": "fail", "message": f"No user with the corresponding username and password exists" }, 
    status=status.HTTP_404_NOT_FOUND)
  
  qr_code = getQRCodeService(user)
  return Response({"qr_code": qr_code},status=status.HTTP_200_OK)

class Verify2FAView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def post(self, request):
        user=request.user
        if user == None:
            return Response({ "status": "Verification failed", "message": f"No user with the corresponding username and password exists"}, 
        status=status.HTTP_404_NOT_FOUND)

        valid_otp = getOTPValidityService(user, request.data.get('otp', None))
        if not valid_otp:
            
            return Response({ "status": "Verification failed", "message": "OTP is invalid or already used" }, 
        status=status.HTTP_400_BAD_REQUEST)
        return Response({ 'otp_verified': True })









class GroupAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data':serializer.data,'message': _('Group created successfully')}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionListAPIView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, format=None):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class GroupPermissionAPIView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, format=None):
        serializer = GroupPermissionSerializer(data=request.data)
        if serializer.is_valid():
            group_id = serializer.validated_data['group_id']
            permission_ids = serializer.validated_data['permission_ids']

            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)

            permissions = Permission.objects.filter(id__in=permission_ids)
            group.permissions.add(*permissions)
            group_serializer = GroupSerializer(group, data=request.data, partial=True)
            return Response({'message': 'Permissions added to the group successfully.'}, status=status.HTTP_200_OK)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserGroupAPIView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, format=None):
        serializer = UserGroupSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            group_ids = serializer.validated_data['group_ids']

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            groups = Group.objects.filter(id__in=group_ids)
            user.groups.add(*groups)

            return Response({'message': 'User added to groups successfully.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            refresh_token=request.data['refresh_token']
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail":"Successfully logged out "},status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
        
        
        
class TokenDestroyView(views.APIView):
    """Use this endpoint to logout user (remove user authentication token)."""

    permission_classes = settings.PERMISSIONS.token_destroy

    def post(self, request):
        user=request.user
        user.logged_in=False
        user.save()
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

    



        
    

    
    