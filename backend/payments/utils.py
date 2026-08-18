from .models import *
from .serializers import *
from django.utils.translation import activate
from django.template.loader import render_to_string
from eLearning import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _

def create_transaction(data):
    ser=TransactionSerializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.save()
    return ser.data

def create_enrollment(data):
    ser=LiveSessionEnrollmentSerializer(data=data)
    ser.is_valid(raise_exception=True)
    enrollment=ser.save()
    return ser.data

def update_account_details(data):
    Account_detail_id=data.pop('Account_detail_id')
    try:
            instance = AcconutDetail.objects.get(pk=Account_detail_id)
    except AcconutDetail.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
    ser = AccountDetailSerializer(instance, data=data,partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return ser.data


def create_account_details(data):
    ser = AccountDetailSerializer( data=data)
    ser.is_valid(raise_exception=True)
    ser.save()
    return ser.data



def send_email_with_template(subject,data,templateName,language_code):
    user= data[0]['user']
    activate(language_code)
    email_html = render_to_string(f'{templateName}.html',{'objects':data})
    send_mail(
        subject=_('Live Session Enrollment'),
        message='',
        html_message=email_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],        
        )



def send_subscribe_email_with_template(data,language_code):
    cycle =data['cycle']
    course=data['course']
    user= data['user']
    activate(language_code)
    # Render the HTML template with the given context
    email_html = render_to_string('course_subscribe.html', {
        'cycle': cycle,
        'course': course,
        'user':user
    })
    print(course)
    # Send the email
    
    send_mail(
        subject=_('Course Subscribtion'),
        message='',
        html_message=email_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
