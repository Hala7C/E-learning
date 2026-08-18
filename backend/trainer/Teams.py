from __future__ import absolute_import, unicode_literals
from .interfaces import IMeeting
from eLearning import settings

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from zoomus import ZoomClient
from decouple import config
import json
from trainer.models import LiveSessionDetails

CLIENT_ID = config("ZOOM_CLIENT_ID")
CLIENT_SECRET = config("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = config("ZOOM_ACCOUNT_ID")


class ZoomMeeting(IMeeting):
    
    def createMeeting(self,user, data ,lsDetails_id) :
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

    def sendNotification(data,user_id) :
        user=data['user']
        groupName=f"user_{user}"
        message="Your Zoom meeting created successfully !!"
        # send_notification_task.delay(group_name,msg)
        data={
            'groupName':groupName,
            'message':message
        }
        return data