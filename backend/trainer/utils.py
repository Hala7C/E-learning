import random 
from django.core.mail import EmailMessage
from eLearning import settings
from time import time
import jwt
import jwt
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from zoomus import ZoomClient
from decouple import config
import json
from trainer.models import LiveSessionDetails
# from newapp.tasks import send_notification_task


import requests

            

"""Go to zoom documentation https://developers.zoom.us/docs/meeting-sdk/apis/#operation/meetingCreate"""


def create_auth_signature(meeting_no, role):
    ZOOM_SDK_CLIENT_ID = CLIENT_ID
    ZOOM_SDK_CLIENT_SECRET = CLIENT_SECRET
    iat = time()
    exp = iat + 60 * 60 * 1  # expire after 1 hour
    oHeader = {"alg": 'HS256', "typ": 'JWT'}
    oPayload = {
        "sdkKey": ZOOM_SDK_CLIENT_ID,
        # The Zoom meeting or webinar number.
        "mn": int(meeting_no),
        # The user role. 0 to specify participant, 1 to specify host.
        "role": role,
        "iat": iat,
        "exp": exp,
        "tokenExp": exp
    }
    jwtEncode = jwt.encode(
        oPayload,
        ZOOM_SDK_CLIENT_SECRET,
        algorithm="HS256",
        headers=oHeader,
    )
    return {'token': jwtEncode, 'sdkKey': ZOOM_SDK_CLIENT_ID}



def create_zoom_user(payload):
    zoom_client = ZoomClient(CLIENT_ID, CLIENT_SECRET,   api_account_id=ACCOUNT_ID)
    response = zoom_client.user.create(
          **payload)
    # if response['result'] == 'success':
    #     created_user_id = response['user_id']
    #     print(f"User created with ID: {created_user_id}")
    #     created_user_id = response['id']
    return response