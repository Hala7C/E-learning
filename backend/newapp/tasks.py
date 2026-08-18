from __future__ import annotations, absolute_import, unicode_literals
from trainer.interfaces import IMeeting
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from zoomus import ZoomClient
from decouple import config
import json
from trainer.models import LiveSessionDetails
from .signals import notification_signal
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMessage
from eLearning import settings

CLIENT_ID = config("ZOOM_CLIENT_ID")
CLIENT_SECRET = config("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = config("ZOOM_ACCOUNT_ID")


@shared_task
def send_notification_task(data):
    group_name=data['groupName']
    message=data['message']
    notification_signal.send(sender=None, message=message, group_name=group_name)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message
        }
    )
    # create notification
    data={
        'message':message,
        'group_name':group_name
    }

# if change sendeing emails in payment to be sended as backgroundJob
@shared_task
def send_subscribe_email_with_template(data):
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
    # Send the email
    send_mail(
        subject=_('Course Subscribtion'),
        message='',
        html_message=email_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    


@shared_task
def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
    

# if change sendeing emails in payment to be sended as backgroundJob
@shared_task
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



class ZoomMeeting(IMeeting):
    @shared_task
    def createMeeting(user, data ,lsDetails_id) :
        """Go to zoom documentation https://developers.zoom.us/docs/meeting-sdk/apis/#operation/meetingCreate"""
        payload = data
        topic = payload['topic']  # Max 100 chars
        agenda = payload['agenda']  # Max 200 chars
        start_time = payload['StartTime']  # %Y-%m-%d %H:%M
        end_time = payload['EndTime']  # %Y-%m-%d %H:%M
        start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        # Perform the subtraction
        time_difference = end_datetime - start_datetime
        # Get the duration in minutes
        duration_minutes = time_difference.total_seconds() / 60
        # ensure the all required values are valid and formated as per zoom documentation
        data = {
            'topic': topic,
            'agenda': agenda,
            'start_time': datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"),
            'topic': topic,
            'type': 2,
            'duration':int(duration_minutes),
            'user_id': "me",  # For user-level apps, pass the me value.
            'settings': {
            'join_before_host': True,
            'waiting_room': False,
            'registrants_email_notification': True,  # Enable email notifications for registrants
            'registrants_confirmation_email': True,
            # Add more settings as needed
            },}
        
        client = ZoomClient(CLIENT_ID, CLIENT_SECRET,   api_account_id=ACCOUNT_ID)
        response = client.meeting.create(**data)
        response_data = response.content.decode('utf-8')
        response_json = json.loads(response_data)
        meeting_url = response_json['start_url']
        data={
            "data":response.json(),
            "url":meeting_url
        }
        ls=LiveSessionDetails.objects.get(pk=lsDetails_id)
        ls.ZoomMeetingURL=meeting_url
        ls.zoomData=response.json()
        ls.save()
        groupName=f"user_{user}"
        message="Your Zoom meeting created successfully !!"
        # send_notification_task.delay(group_name,msg)
        data={
            'groupName':groupName,
            'message':message
        }
        return data
