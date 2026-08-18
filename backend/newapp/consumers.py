import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user=self.scope['user']
        self.group_name= f"user_{user.id}"
        print('-----------------------------------------')
        # self.group_name = 'public_room'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        user=self.scope['user']
        self.group_name= f"user_{user.id}"
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))




