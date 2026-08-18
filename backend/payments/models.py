from django.db import models
from mainAuth.models import CustomUser
from trainer.models import Cycle,Course,LiveSessionDetails
# Create your models here.
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group


class CourseSubscription(models.Model):
    trainee=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='course_subscriptions')
    cycle=models.ForeignKey(Cycle,on_delete=models.CASCADE,related_name='course_subscriptions')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='course_subscriptions')
    subscriptionDateTime=models.DateTimeField(auto_now_add= True)
    def __str__(self):
            return f"CourseSubscription ID: {self.id}"
    class Meta:
        unique_together = ('trainee', 'cycle')

class Transaction(models.Model):
    TYPE_CHOICES=[('withdraw','Withdraw'),('checkout','Checkout')]
    STATUS_CHOICE=[('success','Success'),('failed','Failed'),('cancelled','Cancelled')]
    type=models.CharField(max_length=50 , choices = TYPE_CHOICES )
    status=models.CharField(max_length=100 , choices = STATUS_CHOICE ,default='failed' )
    relatedUser=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='transactions')
    time=models.DateTimeField(auto_now_add= True)
    notes=models.TextField(null=True,blank=True)
    amount=models.DecimalField(max_digits=10, decimal_places=3,null=True,blank=True)
    fee=models.DecimalField(max_digits=10, decimal_places=3,null=True,blank=True)
    def __str__(self):
            return f"Transaction ID: {self.id}"


class LiveSessionEnrollment(models.Model):
    subscriptionId=models.ForeignKey(CourseSubscription,on_delete=models.CASCADE,related_name='enrollments')
    liveSessionDetailId=models.ForeignKey(LiveSessionDetails,on_delete=models.CASCADE,related_name='enrollments')
    transctionId=models.ForeignKey(Transaction,on_delete=models.CASCADE,related_name='enrollments')
    trainer_revenue_percent=models.DecimalField(max_digits=5, decimal_places=2)
    def __str__(self):
        return f"Enrollment ID: {self.id}"


class Config(models.Model):
    trainer_percent=models.DecimalField(max_digits=5, decimal_places=2)
    created_on=models.DateTimeField(auto_now_add=True)



class AcconutDetail(models.Model):
    trainer=models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='acconutDetail')
    connect_account = models.CharField(max_length=100,null=True,blank=True)
    access_token=models.CharField(max_length=150,null=True,blank=True)
    balance=models.DecimalField(max_digits=10, decimal_places=3,default=0.0)
    def clean(self):
        super().clean()
        group_name = 'Trainer'
        if self.trainer and not self.trainer.groups.filter(name=group_name).exists():
            raise ValidationError(f"The user must be a Trainer .")
    @property
    def owner(self):
        return self.trainer


class Payout(models.Model):
    payout_status=[
        (('is_approved'),('is_approved')),
        (('pending'),('pending')),
        (('refused'),('refused')),
    ]
    trainer = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name='user')
    amount =models.IntegerField()
    status=models.CharField(max_length=50 ,choices =payout_status,null=True, blank=True)
    @property
    def owner(self):
        return self.trainer

