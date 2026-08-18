from rest_framework import serializers
from mainAuth.models import CustomUser
from trainer.models import Course,Cycle,LiveSessionDetails
from .models import *
from django.db.models import Sum, Q
class CourseSubscrubtionSerializer(serializers.HyperlinkedModelSerializer):
    trainee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    cycle = serializers.PrimaryKeyRelatedField(queryset=Cycle.objects.all())
    course=serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
            model = CourseSubscription
            fields=['id','trainee','cycle','course','subscriptionDateTime']


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    relatedUser=serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
            model = Transaction
            fields=['id','type','status','relatedUser','time','notes','amount']
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     total_checkout_transaction =  Transaction.objects.filter(Q(status='success') & Q(type='checkout') ).aggregate(total_checkout=Sum('amount'))['total_checkout'] or 0
    #     total_withdraw_transaction =  Transaction.objects.filter(Q(status='success') & Q(type='withdraw') ).aggregate(total_withdraw=Sum('amount'))['total_withdraw'] or 0
    #     total_fees =  Transaction.objects.filter(Q(status='success') & Q(type='checkout') ).aggregate(total_fees=Sum('fee'))['total_fees'] or 0
    #     representation['total_checkout_transaction']=total_checkout_transaction      
    #     representation['total_withdraw_transaction']=total_withdraw_transaction      
    #     representation['total_fees']=total_fees      
    #     return representation
            



class LiveSessionEnrollmentSerializer(serializers.HyperlinkedModelSerializer):
    subscriptionId=serializers.PrimaryKeyRelatedField(queryset=CourseSubscription.objects.all())
    liveSessionDetailId=serializers.PrimaryKeyRelatedField(queryset=LiveSessionDetails.objects.all())
    transctionId=serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all())
    class Meta:
            model = LiveSessionEnrollment
            fields=['id','subscriptionId','liveSessionDetailId','transctionId','trainer_revenue_percent']
            
            


class ConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model= Config
        fields=['id','trainer_percent','created_on']


class AccountDetailSerializer(serializers.HyperlinkedModelSerializer):
    trainer=serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model=AcconutDetail
        fields=['trainer', 'connect_account', 'access_token', 'balance']

class PayoutSerializer(serializers.HyperlinkedModelSerializer):
    trainer=serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
         model=Payout
         fields=['id','trainer','amount','status']
    