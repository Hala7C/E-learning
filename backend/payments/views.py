from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import *
from decimal import Decimal
import urllib
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
from django.conf import settings
from django.shortcuts import redirect
import requests
from django.db.models import Sum, Q
from .models import AcconutDetail
from rest_framework.response import Response
from .serializers import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from eLearning import settings
import stripe
from datetime import datetime
from newapp.tasks import send_normal_email
from django.db.models import F, Sum
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
from trainer.models import LiveSessionMainDataSection
from django.db.models import Sum
from .utils import *
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
# from newapp.tasks import send_subscribe_email_with_template,send_email_with_template
from .utils import send_email_with_template,send_subscribe_email_with_template
from django.utils.translation import activate
from rest_framework.decorators import api_view
from django.http.response import JsonResponse, HttpResponse
from django.views.generic.base import TemplateView
from django.http.response import JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
import requests
import json
import ast
from mainAuth.validators import validate_month,validate_year
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user
from .models import *
from .serializers import *
from django.utils.translation import get_language
from django.utils.translation import get_language
from .enum import PayoutStatus
from .filters import TransactionsFilter
User=get_user_model()
from .permissions import *
from .models import *
from django.db.models.functions import Coalesce
class HomePageView(TemplateView):
    template_name = 'home.html' 

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    

class CreateCheckoutApiView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,*args, **kwargs):
        language_code = get_language()
        live_session_list=request.data.pop('live_session_list',[])
        subscriptionID=request.data.pop('subscriptionID')
        user=request.user
        print(language_code)
        domain_url = 'http://127.0.0.1:8000/en/api/payment/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:

            line_items = []
            amount=0
            for item in live_session_list:
                liveSessionDetails = LiveSessionDetails.objects.get(id=item)
                price = liveSessionDetails.price
                line_item = {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(price) * 100,
                        'product_data': {
                            'name': liveSessionDetails.liveSessionMainDataID.title,
                            'description': liveSessionDetails.liveSessionMainDataID.description
                        },
                    },
                    'quantity': 1,
                    
                }
                amount=amount+price
                line_items.append(line_item)
            print(line_items)
            payload={
                    'relatedUser':user.id ,
                    'type':'checkout',
                    'amount': amount
                }
            transaction=create_transaction(payload)
            checkout_session = stripe.checkout.Session.create(
                
                payment_method_types=['paypal','card'],
                mode='payment',
                line_items=line_items,
                metadata={
                    'liveSessionDetails_id': str(live_session_list),
                    'subscriptionID':subscriptionID,
                    'user_id':user.id,
                    'language_code':language_code,
                    'transaction_id':transaction['id'],
                },
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}&transaction_id={transaction.id}',
                cancel_url=domain_url + 'cancelled/?transaction_id='+f"{transaction['id']}",
                customer_email=user.email,
            )

            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelledView(TemplateView):
    template_name = 'cancelled.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_id = self.request.GET.get('transaction_id')
        context['transaction_id'] = transaction_id
        transaction=Transaction.objects.get(id=transaction_id)
        transaction.status='cancelled'
        transaction.save()
        print(transaction_id)
        return context

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    try:
        if event['type'] == 'checkout.session.completed':
            payload = json.loads(request.body)
            metadata = payload['data']['object']['metadata']
            # payment_intent = stripe.PaymentIntent.retrieve(
            #     payload['data']['object']['payment_intent']
            # )
            payment_intent = stripe.PaymentIntent.retrieve(
            payload['data']['object']['payment_intent'],
            expand=['latest_charge.balance_transaction'],
            )
            fee_details = payment_intent.latest_charge.balance_transaction.fee_details
            print(f"fee_details {fee_details}")
            liveSessionDetails_id = metadata.get('liveSessionDetails_id')
            subscription_id = metadata.get('subscriptionID')
            user_id=metadata.get('user_id')
            user=User.objects.get(id=user_id)
            language_code=metadata.get('language_code')
            transaction_id=metadata.get('transaction_id')
            # transaction
            transaction=Transaction.objects.get(id=transaction_id)
            transaction.status='success'
            transaction.fee=(fee_details[0].amount)/100
            transaction.save()

            # enrollment
            trainer_percent=Config.objects.all().last()
            liveSessionDetails_id_list = ast.literal_eval(liveSessionDetails_id)
            for ls in liveSessionDetails_id_list:
                create_enroll={
                        'subscriptionId':subscription_id,
                        'liveSessionDetailId':ls,
                        'transctionId': transaction.id,
                        'trainer_revenue_percent':float(trainer_percent.trainer_percent)
                                }
                enrollment=create_enrollment(create_enroll)
                liveSessionDetail=LiveSessionDetails.objects.get(id=ls)

                # get trainer and add total amount to trainer balance
                trainer=liveSessionDetail.liveSessionMainDataID.course.trainer
                Account_detail=AcconutDetail.objects.filter(trainer=trainer)
                amount=liveSessionDetail.price * trainer_percent.trainer_percent
                if Account_detail.exists():
                    Account_detail=AcconutDetail.objects.get(trainer=trainer)
                    old_balance=Account_detail.balance
                    new_balance= old_balance + amount
                    account_detail={
                    'Account_detail_id':Account_detail.id,
                    'trainer':trainer.id,
                    'balance':float(new_balance)
                    }
                    accountDetails=update_account_details(account_detail)
                else:
                    new_balance=amount
                    account_detail={
                    'trainer':trainer.id,
                    'balance':float(new_balance)
                    }
                    account_details=create_account_details(account_detail)
            
                print("Payment was successful.")
            # send email
            enrollments=LiveSessionEnrollment.objects.filter(transctionId=transaction.id)
            subject='Live Session Enrollment'
            objects=[]
            for enrollment in enrollments:
                liveSessionDetailId=enrollment.liveSessionDetailId
                liveSessionMainData1=liveSessionDetailId.liveSessionMainDataID
                liveSessionMainData=LiveSessionMainDataSection.objects.language(language_code).get(id=liveSessionMainData1.id)
                course=Course.objects.language(language_code).get(id=liveSessionMainData.course.id)
                zoom_dict=liveSessionDetailId.zoomData
                zoom_password=zoom_dict['password']
                zoom_url=zoom_dict['join_url']
                data={
                    'user':user,
                    'liveSessionDetail':liveSessionDetailId,
                    'liveSessionMainData':liveSessionMainData,
                    'course':course,
                    'zoom_url':zoom_url,
                    'zoom_password':zoom_password,
                    'language_code':language_code
                    }
                objects.append(data)
            templateName='enrollment_details'
            send_email_with_template(subject=subject,data=objects,templateName=templateName,language_code=language_code)
            print('email sended......')
            

        if event['type'] == 'payment_intent.payment_failed':
            payment_intent_id = event['data']['object']['id']
            checkout_session = stripe.checkout.Session.list(payment_intent=payment_intent_id, limit=1)
            if checkout_session.data:
                metadata = checkout_session.data[0]['metadata']
            user_id=metadata.get('user_id')
            transaction_id=metadata.get('transaction_id')
            print(f"user {user_id}")
            user=User.objects.get(id=user_id)
            transaction=Transaction.objects.get(id=transaction_id)
            transaction.status='failed'
            transaction.save()
            print('payment failed')
            
    except requests.exceptions.RequestException as e:
    # Handle request-related exceptions
        print("Request exception:", e)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (status codes >= 400)
        print("HTTP error:", e)

    except Exception as e:
        # Handle other types of exceptions
        print("Exception:", e)
    return HttpResponse(status=200)


stripe.api_key = settings.STRIPE_SECRET_KEY



class CourseSubscrubtionViewSet(ModelViewSet):
    serializer_class=CourseSubscrubtionSerializer
    queryset=CourseSubscription.objects.all()
    permission_classes=[CourseSubscrubtionPolicy]
    def create(self,request,*args, **kwargs):
        request = self.request
        language_code = get_language()    
        user=request.user
        request.data['trainee']=user.id
        ser=CourseSubscrubtionSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            cycle=Cycle.objects.get(pk=request.data['cycle'])
            course=Course.objects.language(language_code).get(pk=request.data['course'])
            data={
                'user':user,
                'cycle':cycle,
                'course':course
            }
            send_subscribe_email_with_template(data,language_code)
            return Response(ser.data,status=status.HTTP_201_CREATED)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False,methods=['Post'])
    def unsubscribe(self,request,*args, **kwargs):
        user=request.user
        language_code = get_language()
        request.data['trainee']=user.id
        cycle=Cycle.objects.get(pk=request.data['cycle'])
        course=Course.objects.language(language_code).get(pk=request.data['course'])
        courseSubscription=CourseSubscription.objects.filter(trainee=user)
        print(courseSubscription.id)
        courseSubscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class TransactionViewSet(ModelViewSet):
    serializer_class=TransactionSerializer
    queryset=Transaction.objects.all()
    permission_classes=[TransactionPolicy]
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')
        ordering = self.request.query_params.get('ordering')
        if ordering == 'date':
            queryset = queryset.order_by('time')
        elif ordering == '-date':
            queryset = queryset.order_by('-time')
        if user :
            queryset=queryset.filter(relatedUser=user)
        if day :
            if not month:
                month = datetime.now().month
            queryset=queryset.annotate(
            day=ExtractDay('time'),
            month=ExtractMonth('time')).filter(day=day,month=month)
        if month :
            queryset=queryset.annotate(
            month=ExtractMonth('time')).filter(month=month)
        return queryset
    def list(self,request):
        transactions=Transaction.objects.all()
        serializer = self.serializer_class(transactions,many=True)
        total_checkout_transaction =  Transaction.objects.filter(Q(status='success') & Q(type='checkout') ).aggregate(total_checkout=Sum('amount'))['total_checkout'] or 0
        total_withdraw_transaction =  Transaction.objects.filter(Q(status='success') & Q(type='withdraw') ).aggregate(total_withdraw=Sum('amount'))['total_withdraw'] or 0
        total_fees =  Transaction.objects.filter(Q(status='success') & Q(type='checkout') ).aggregate(total_fees=Sum('fee'))['total_fees'] or 0
        response_data = {
            'total_checkout_transaction': total_checkout_transaction,
            'total_withdraw_transaction': total_withdraw_transaction,
            'total_fees': total_fees,
            'results': serializer.data
        }
        return Response({"data":response_data},status=status.HTTP_200_OK)
    
    def post(self,request,*args, **kwargs):
        ser=TransactionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data,status=status.HTTP_200_OK)



class EnrollmentViewSet(ModelViewSet):
    serializer_class=LiveSessionEnrollmentSerializer
    queryset=LiveSessionEnrollment.objects.all()
    permission_classes=EnrollmentPolicy
    def create(self,request,*args, **kwargs):
        language_code = get_language()
        ser=LiveSessionEnrollmentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        enrollment=ser.save()
        return Response(ser.data,status=status.HTTP_200_OK)


class AccountDetailViewSet(ModelViewSet):
    permission_classes=[AccountDetailPolicy]
    serializer_class=AccountDetailSerializer
    queryset=AcconutDetail.objects.all()
    def reCalculateBalance(self,request,*args, **kwargs):
        user=request.user
        success_transactions = Transaction.objects.filter(user_id=user.id, type='success')
        total_balance = LiveSessionEnrollment.objects.filter(transctionId__in=success_transactions).aggregate(Sum('trainer_revenue_percent'))['trainer_revenue_percent__sum']
        account_detail=AcconutDetail.objects.get(trainer=user)
        return account_detail == total_balance
    @action(detail=True, methods=['get'])
    def get_revenue(self,request,*args, **kwargs):
        trainer=request.user
        enrollments = LiveSessionEnrollment.objects.filter(
        liveSessionDetailId__liveSessionMainDataID__course__trainer=trainer.id,
        transctionId__status='success'
            )
        course_id = request.GET.get('course_id') 
        year=request.GET.get('year') 
        month=request.GET.get('month') 
        
        if  course_id is not None:
            enrollments = enrollments.filter(liveSessionDetailId__liveSessionMainDataID__course__id=course_id)
        if month is not None:
            current_year = datetime.now().year
            enrollments = enrollments.annotate(
            year=ExtractYear('transctionId__time'),
            month=ExtractMonth('transctionId__time')
                ).filter(month=month,year=current_year)
        if year is not None:
            enrollments = enrollments.annotate(
            year=ExtractYear('transctionId__time')
        ).filter(year=year)
        enrollments = enrollments.annotate(
            revenue=F('trainer_revenue_percent') * (F('liveSessionDetailId__price') - Coalesce(F('transctionId__fee'), Decimal('0.0')) )
        )
        result=[]
        for enrollment in enrollments:
            CourseSubscription_id=enrollment.subscriptionId.id
            Subscribe=CourseSubscription.objects.get(pk=CourseSubscription_id)
            course=Course.objects.get(pk=Subscribe.course.id)
            data={
                "course":Subscribe.course.title,
                "cycle":Subscribe.cycle.NumberCycle,
                "live_main":enrollment.liveSessionDetailId.liveSessionMainDataID.title,
                "trainee":Subscribe.trainee.email,
                "revenue":enrollment.revenue
            }
            result.append(data)
        total_revenue = enrollments.aggregate(total_revenue=Sum('revenue'))['total_revenue']
        result.append({'total_revenue':total_revenue})
        return Response({'data':result},status=status.HTTP_200_OK)
    @action(detail=True, methods=['get'])
    def get_balance(self,request,*args, **kwargs):
        trainer=request.user
        Account_detail=AcconutDetail.objects.get(trainer=trainer)
        balance=Account_detail.balance
        return Response({'balance':balance},status=status.HTTP_200_OK)
    @action(detail=True, methods=['get'])
    def get_trainer_transactions(self,request,*args, **kwargs):
        trainer=request.user
        transactions=Transaction.objects.filter(relatedUser=trainer,type='withdraw',status='success')
        ser=TransactionSerializer(transactions,many=True)
        return Response(ser.data,status=status.HTTP_200_OK)
    @action(detail=True, methods=['get'])
    def get_total_trainer_transactions(self,request,*args, **kwargs):
        trainer=request.user
        year=request.GET.get('year') 
        month=request.GET.get('month')
        transactions=Transaction.objects.filter(relatedUser=trainer,type='withdraw',status='success') 
        if month  is not None:
            print('month')
            current_year = datetime.now().year
            transactions = transactions.annotate(
            year=ExtractYear('time'),
            month=ExtractMonth('time')
                ).filter(month=month,year=current_year)
        if year is not None:
            print('year')
            transactions = transactions.annotate(
            year=ExtractYear('time')
        ).filter(year=year)
        total_payouts = transactions.aggregate(total_payouts=Sum('amount'))['total_payouts']
        ser=TransactionSerializer(transactions,many=True)
        data={
            'transactions':ser.data,
            'total_payouts':total_payouts
        }
        return Response(data,status=status.HTTP_200_OK)








def create_stripe_payout(payout, request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:        
        payout_amount = payout.amount
        
        user = payout.trainer
        account_detail = AcconutDetail.objects.get(trainer=user)
        bank_account_token_id=account_detail.connect_account
        print(f'connect account {bank_account_token_id}')
        if account_detail.balance < payout_amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        payout_obj = stripe.Transfer.create(
            amount=payout_amount, 
            currency='EUR',
            destination=bank_account_token_id,
        )
        payout.status = "is_approved"
        payout.save()
        payload={
                    'relatedUser':user.id ,
                    'type':'withdraw',
                    'status':'success',
                    'amount': payout_amount
                }
        transaction=create_transaction(payload)
        # TODO :add all notification type 
        email_body=f'your withdraw request on <elearnin> is  {payout.status} '
        data={
                'email_body':email_body,
                'email_subject':"Withdraw Request Resualt",
                'to_email':user.email
            }
        # send_normal_email.delay(data=data)
        return Response({'message': 'Payout initiated successfully , the fund will appear in your bank account within a day '}, status=status.HTTP_201_CREATED)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PayoutViewSet(ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    permission_classes=[PayoutPolicy]
    ordering_fields = ['pending','approved','refused']
    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('filter')
        if ordering == 'pending':
            queryset = queryset.filter(status='pending')
        elif ordering == 'approved':
            queryset = queryset.filter(status='is_approved')
        elif ordering == 'refused':
            queryset = queryset.filter(status='refused')
        return queryset
    def create(self, request, *args, **kwargs):
        required_fields = { "amount"}
        if set(request.data.keys()) != required_fields:
            return Response(
                {"error": "Please provide  'amount' fields only"},
                status=status.HTTP_400_BAD_REQUEST
            )
        payout_amount = request.data["amount"]
        user = request.user
        account_detail = AcconutDetail.objects.get(trainer=user)
        if account_detail.balance < payout_amount:
            return Response({'error': 'Insufficient trainer balance'}, status=status.HTTP_400_BAD_REQUEST)
        request.data["status"] = "pending"
        request.data["trainer"] = request.user.id
        return super().create(request, *args, **kwargs)
    
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk):
     try:
        payout = Payout.objects.get(pk=pk)
        new_status = request.data.get('status')
        if not PayoutStatus.has_value(new_status):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


        if new_status ==  PayoutStatus.IS_APPROVED.value:
            
            return create_stripe_payout(payout, request)
            
        else:
            payout.status = new_status
            payout.save()
            return Response({'message': 'Payout status updated successfully'}, status=status.HTTP_200_OK)

     except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






class StripeAuthorizeView(APIView):
    permission_classes=[IsTrainerUser]
    def get(self, request):
        print(f'fff{request.user.id}')
        url = 'https://connect.stripe.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'scope': 'read_write',
            'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
            'state':request.user.id,
            'redirect_uri': f'http://127.0.0.1:8000/en/api/payment/oauth/callback'
        }
        url = f'{url}?{urllib.parse.urlencode(params)}'
        return Response(url,status=status.HTTP_200_OK)
        return redirect(url)


class StripeAuthorizeCallbackView(APIView):
    # put isTrainer fpr permission
    permission_classes=[AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        user_id  = request.GET.get('state')

        # Retrieve the user object using the authentication token
        user = User.objects.get(pk=user_id)
        print(user)
        if code:
            data = {
                'client_secret': settings.STRIPE_SECRET_KEY,
                'grant_type': 'authorization_code',
                'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
                'code': code
            }
            url = 'https://connect.stripe.com/oauth/token'
            resp = requests.post(url, params=data)
            print(resp.json())
        # add stripe access token and stripe user account id
        stripe_user_id = resp.json()['stripe_user_id']
        stripe_access_token = resp.json()['access_token']
        
        try:
            account_detail=user.acconutDetail
            account_detail.connect_account=stripe_user_id
            account_detail.access_token=stripe_access_token
            account_detail.save()
        except AcconutDetail.DoesNotExist as e:
            data={
                "trainer":user.id,
                "connect_account":stripe_user_id,
                "access_token":stripe_access_token
            }
            account_detail=create_account_details(data)
            print("added")
        url = reverse('home')
        response = redirect(url)
        return response
