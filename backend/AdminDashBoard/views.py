from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from mainAuth.serializers import UserRegistrationSerializer,GroupSerializer,GroupPermissionSerializer,UserGroupSerializer,PermissionSerializer,TrainerSerializer,StudentSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission,Group
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
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
from mainAuth.validators import validate_month,validate_year
from trainer.models import Course
from django.db.models.functions import Coalesce
from decimal import Decimal
# Create your views here.
from mainAuth.permissions import IsAdminUser
# from rest_framework.permissions import IsAdminUser
from django.core.exceptions import ValidationError


class DashbordViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class= UserRegistrationSerializer
    permission_classes=[IsAdminUser]
    @action(methods=['post'],detail=False)
    def list_user_in_date(self,request):
        date_string = request.data['date']
        try:
            date_to_compare = datetime.strptime(date_string, "%Y-%m-%d")
            year = date_to_compare.year
            month = date_to_compare.month
            if month:
                month_date = validate_month(month)
            if year:
                year_date = validate_year(year)
        except ValidationError as e:
            raise e
        # Query the database for rows with the same year and month
        results = User.objects.annotate(
            year=ExtractYear('date_joined'),
            month=ExtractMonth('date_joined')
        ).filter(year=year, month=month).count()
        return Response({"data":results},status=status.HTTP_200_OK)
    

    @action(methods=['post'],detail=False)
    def list_user_type_in_date(self, request):
        date_string = request.data.get('date')
        try:
            date_to_compare = datetime.strptime(date_string, "%Y-%m-%d")
            year = date_to_compare.year
            month = date_to_compare.month
            if month:
                month_date = validate_month(month)
            if year:
                year_date = validate_year(year)
        except ValidationError as e:
            raise e
        results = User.objects.annotate(
            year=ExtractYear('date_joined'),
            month=ExtractMonth('date_joined')
        ).filter(year=year, month=month).values('groups__name').annotate(count=Count('id'))
        data = {group['groups__name']: group['count'] for group in results}
        return Response({"data": data}, status=status.HTTP_200_OK)

    @action(methods=['get'],detail=True)
    def default_user_statistic(self,request):
        cats=User.objects.count()
        return Response({"all users":cats},status=status.HTTP_200_OK)

    def type_user_statistic(self, request):
        user_groups = User.objects.values('groups__name').annotate(count=Count('id')).order_by('groups__name')
        
        data = {group['groups__name']: group['count'] for group in user_groups}
        
        return Response({"data": data}, status=status.HTTP_200_OK)
    

    @action(methods=['get'],detail=True)    
    def default_date_join_user_statistic(self,request):
        month= request.GET.get('month')
        year= request.GET.get('year')
        try:
            if month:
                month_date = validate_month(month)
            if year:
                year_date = validate_year(year)
        except ValidationError as e:
            raise e
        admins=CustomUser.objects.filter(date_joined__month= month,date_joined__year=year).count()
        return Response({"data":admins},status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def block_user(self, request, pk):
        user = get_user_model()
        try:
            user = CustomUser.objects.get(pk=pk)
            user.is_active = False
            user.save()
            return Response({"active": False}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['get'], detail=True)
    def list_blocked_user(self, request):
        block_users = User.objects.filter(is_active=False).values('id','email') 
        return Response(block_users, status=status.HTTP_200_OK)


    @action(methods=['get'], detail=True)
    def unblock_user(self, request, pk):
        user = get_user_model()
        try:
            user = CustomUser.objects.get(pk=pk)
            user.is_active = True
            user.save()
            return Response({"active": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)        


    @action(methods=['get'], detail=True)
    def list_active_user(self, request):
        active_users = User.objects.filter(is_active=True).values('id','email') 
        return Response(active_users, status=status.HTTP_200_OK)
    


    @action(detail=True, methods=['get'])
    def users_joined_last_month(self, request):
        current_date = datetime.now()
        previous_month = (current_date.month - 1) % 12 or 12  
        admins = CustomUser.objects.filter(date_joined__month=previous_month).count()
        return Response({"users_joined_last_month": admins}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'])
    def users_joined_last_three_month(self, request):
        current_date = timezone.now()
        three_months_ago = current_date - timedelta(days=3*30)  # Assuming a month has 30 days
        admins = CustomUser.objects.filter(date_joined__gte=three_months_ago)
        admins_count = admins.count()
        print(three_months_ago)
        return Response({"users_joined_last_three_month": admins_count}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'])
    def users_joined_last_year(self, request):
        current_date = timezone.now()
        one_year_ago = current_date - timedelta(days=365)  # Assuming a year has 365 days
        print(one_year_ago)
        admins = CustomUser.objects.filter(date_joined__gte=one_year_ago)
        print(admins)
        admins_count = admins.count()
        return Response({"users_joined_last_year": admins_count}, status=status.HTTP_200_OK)  


    @action(detail=True, methods=['get'])    
    def list_students(self,request,*args, **kwargs):
        group = Group.objects.get(name='Student')
        users = group.user_set.all()
        data=StudentSerializer(users,many=True)
        return Response(data=data.data,status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])    
    def list_trainers(self,request,*args, **kwargs):
        group = Group.objects.get(name='Trainer')
        users = group.user_set.all()
        data=TrainerSerializer(users,many=True)
        return Response(data=data.data)
    
    @action(detail=True, methods=['get'])    
    def student_information(self,request,pk):
        try:
            user = User.objects.get(pk=pk)
            if not user.groups.filter(name='Student').exists():
                return Response({'error': 'this user in not a student'}, status=status.HTTP_400_BAD_REQUEST)
            data=StudentSerializer(user)
        except User.DoesNotExist as e:
            return Response({'error':'object not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data.data )
    
    @action(detail=True, methods=['get'])    
    def trainer_information(self,request,pk):
        try:
            user = User.objects.get(pk=pk)
            if not user.groups.filter(name='Trainer').exists():
                return Response({'error': 'this user in not a trainer'}, status=status.HTTP_400_BAD_REQUEST)
            data=TrainerSerializer(user)
        except User.DoesNotExist as e:
            return Response({'error':'object not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data.data )

    def list_courses(self,request):
        course=Course.objects.count()
        return Response({"all courses":course},status=status.HTTP_200_OK)
    
    def list_cycles(self,request):
        cycle=Cycle.objects.count()
        return Response({"all Cycles":cycle},status=status.HTTP_200_OK)
    
    def course_per_category(self,request):
        categories_with_course_count = Category.objects.annotate(num_courses=Count('courses'))
        data = [{"category": category.name, "num_courses": category.num_courses} for category in categories_with_course_count]
        return Response({"categories": data}, status=status.HTTP_200_OK)
    


    @action(detail=True, methods=['put'])    
    def disable_course(self,request, pk):
        course = Course.objects.get(pk=pk)
        course.is_blocked = True
        course.save()
        return Response(data={'message':'course disabled successfully'} )
    @action(detail=True, methods=['put'])    
    def enable_course(self,request, pk):
        course = Course.objects.get(pk=pk)
        course.is_blocked = False
        course.save()
        return Response(data={'message':'course enabled successfully'} )
    @action(detail=True, methods=['get'])    
    def finicial_data(self,request,*args, **kwargs ):
        year = request.GET.get('year')
        month = request.GET.get('month')
        course_id = request.GET.get('course_id')
        try:
            if month:
                month_date = validate_month(month)
            if year:
                year_date = validate_year(year)
            if course_id:
                course_id=Course.objects.get(pk=course_id)
        except ValidationError as e:
            raise e
        except Course.DoesNotExist:
            raise ValidationError({'id': f'Object with ID "{course_id}" does not exist.'})
        transactions = self.get_total_money(year, month)
        total_money = transactions.aggregate(total_payouts=Sum('amount'))['total_payouts'] or 0
        total_fees = transactions.aggregate(total_fees=Sum('fee'))['total_fees'] or 0

        enrollments = self.get_total_revenue(course_id, year, month)
        total_trainer_revenue = enrollments['total_trainer_revenue'].aggregate(total_revenue=Sum('revenue'))['total_revenue'] or 0
        total_site_revenue = enrollments['total_site_revenue'].aggregate(total_revenue=Sum('revenue'))['total_revenue'] or 0

        total_withdrawals = self.get_total_withdrawals(year, month)

        data = {
            'total_money': total_money,
            'total_fees': total_fees,
            'total_site_revenue': total_site_revenue,
            'total_trainer_revenue':total_trainer_revenue,
            "trainer's withdrawals": total_withdrawals
        }
        return Response(data )

    def get_total_money(self, year=None, month=None):
        transactions = Transaction.objects.filter(status='success',type='checkout')
        if month is not None:
            current_year = datetime.now().year
            transactions = transactions.annotate(
                year=ExtractYear('time'),
                month=ExtractMonth('time')
            ).filter(month=month, year=current_year)
        if year is not None:
            transactions = transactions.annotate(
                year=ExtractYear('time')
            ).filter(year=year)
        return transactions

    def get_total_revenue(self, course_id=None, year=None, month=None):
        enrollments = LiveSessionEnrollment.objects.filter(transctionId__status='success',transctionId__type='checkout')
        if course_id is not None:
            enrollments = enrollments.filter(liveSessionDetailId__liveSessionMainDataID__course__id=course_id)
        if month is not None:
            current_year = datetime.now().year
            enrollments = enrollments.annotate(
                year=ExtractYear('transctionId__time'),
                month=ExtractMonth('transctionId__time')
            ).filter(month=month, year=current_year)
        if year is not None:
            enrollments = enrollments.annotate(
                year=ExtractYear('transctionId__time')
            ).filter(year=year)
        
        total_trainer_revenue= enrollments.annotate(revenue= F('trainer_revenue_percent') * (F('liveSessionDetailId__price') - Coalesce(F('transctionId__fee'), Decimal('0.0')) ))
        total_site_revenue= enrollments.annotate(revenue=(1 - F('trainer_revenue_percent')) * (F('liveSessionDetailId__price')- Coalesce(F('transctionId__fee'), Decimal('0.0')) ))
        return {'total_trainer_revenue':total_trainer_revenue,'total_site_revenue':total_site_revenue}

    def get_total_withdrawals(self, year=None, month=None):
        transactions = Transaction.objects.filter(type='withdraw', status='success')
        if month is not None:
            current_year = datetime.now().year
            transactions = transactions.annotate(
                year=ExtractYear('time'),
                month=ExtractMonth('time')
            ).filter(month=month, year=current_year)
        if year is not None:
            transactions = transactions.annotate(
                year=ExtractYear('time')
            ).filter(year=year)
        return transactions.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

