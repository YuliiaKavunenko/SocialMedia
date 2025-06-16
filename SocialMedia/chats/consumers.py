import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, ChatMessage
from user.models import Profile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        author_id = self.scope['user'].profile.id
        
        await self.save_message(author_id, self.chat_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author_id': author_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'author_id': event['author_id'],
        }))

    @database_sync_to_async
    def save_message(self, author_id, chat_id, message):
        author = Profile.objects.get(id=author_id)
        chat = ChatGroup.objects.get(id=chat_id)
        return ChatMessage.objects.create(
            author=author,
            chat_group=chat,
            content=message
        )
