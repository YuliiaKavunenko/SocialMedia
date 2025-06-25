import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from .models import ChatGroup, ChatMessage
from user.models import Profile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Проверяем аутентификацию
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user_group_name = f'user_{self.scope["user"].id}'

        # Проверяем доступ к чату
        has_access = await self.check_chat_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

        # Обновляем статус пользователя как онлайн в кэше
        await self.update_user_online_status(True)
        
        # Отправляем обновление онлайн статуса всем участникам чата
        await self.broadcast_online_status_update()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        
        # Обновляем статус пользователя как оффлайн в кэше
        await self.update_user_online_status(False)
        
        # Отправляем обновление онлайн статуса всем участникам чата
        await self.broadcast_online_status_update()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'text')
            
            # Получаем профиль пользователя
            user_profile = await self.get_user_profile()
            if not user_profile:
                return

            if message_type == 'get_online_status':
                # Отправляем текущий онлайн статус
                await self.send_online_status()
                return

            if message_type == 'text':
                message = data['message'].strip()
                if not message:
                    return

                # Сохраняем текстовое сообщение
                saved_message = await self.save_message(user_profile.id, self.chat_id, message)
                if not saved_message:
                    return

                # Получаем информацию о чате и авторе
                chat_info = await self.get_chat_info(self.chat_id)
                author_info = await self.get_author_info(user_profile.id)

                # Отправляем сообщение в группу чата
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'author_id': user_profile.id,
                        'author_name': author_info['name'],
                        'author_avatar': author_info['avatar'],
                        'sent_at': saved_message.sent_at.strftime('%H:%M'),
                        'date': saved_message.sent_at.strftime('%Y-%m-%d'),
                        'message_type': 'text'
                    }
                )

                # Отправляем обновление списка чатов всем участникам
                for member_id in chat_info['members']:
                    await self.channel_layer.group_send(
                        f'user_{member_id}',
                        {
                            'type': 'chat_list_update',
                            'chat_id': self.chat_id,
                            'chat_name': await self.get_chat_display_name(self.chat_id, member_id),
                            'last_message': message,
                            'last_message_time': saved_message.sent_at.strftime('%H:%i'),
                            'is_personal': chat_info['is_personal']
                        }
                    )

            elif message_type == 'image':
                image_data = data.get('image')
                caption = data.get('caption', '').strip()
                
                if not image_data:
                    return

                # Сохраняем сообщение с изображением
                saved_message = await self.save_image_message(
                    user_profile.id, 
                    self.chat_id, 
                    caption, 
                    image_data
                )
                if not saved_message:
                    return

                # Получаем информацию о чате и авторе
                chat_info = await self.get_chat_info(self.chat_id)
                author_info = await self.get_author_info(user_profile.id)

                # Отправляем сообщение в группу чата
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': caption,
                        'author_id': user_profile.id,
                        'author_name': author_info['name'],
                        'author_avatar': author_info['avatar'],
                        'sent_at': saved_message.sent_at.strftime('%H:%M'),
                        'date': saved_message.sent_at.strftime('%Y-%m-%d'),
                        'message_type': 'image',
                        'image_url': saved_message.attached_image.url if saved_message.attached_image else None
                    }
                )

                # Отправляем обновление списка чатов всем участникам
                display_message = caption if caption else "Фото"
                for member_id in chat_info['members']:
                    await self.channel_layer.group_send(
                        f'user_{member_id}',
                        {
                            'type': 'chat_list_update',
                            'chat_id': self.chat_id,
                            'chat_name': await self.get_chat_display_name(self.chat_id, member_id),
                            'last_message': display_message,
                            'last_message_time': saved_message.sent_at.strftime('%H:%i'),
                            'is_personal': chat_info['is_personal']
                        }
                    )

        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'author_id': event['author_id'],
            'author_name': event['author_name'],
            'author_avatar': event['author_avatar'],
            'sent_at': event['sent_at'],
            'date': event['date'],
            'message_type': event['message_type'],
            'image_url': event.get('image_url')
        }))

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_list_update',
            'chat_id': event['chat_id'],
            'chat_name': event['chat_name'],
            'last_message': event['last_message'],
            'last_message_time': event['last_message_time'],
            'is_personal': event['is_personal']
        }))

    async def online_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_status',
            'is_personal_chat': event['is_personal_chat'],
            'is_online': event.get('is_online', False),
            'last_seen': event.get('last_seen'),
            'online_count': event.get('online_count', 0),
            'total_members': event.get('total_members', 0)
        }))

    async def send_online_status(self):
        """Отправляем текущий онлайн статус для чата"""
        chat_info = await self.get_chat_info(self.chat_id)
        user_profile = await self.get_user_profile()
        
        if chat_info['is_personal']:
            # Для персонального чата показываем статус собеседника
            other_member_id = None
            for member_id in chat_info['members']:
                if member_id != self.scope["user"].id:
                    other_member_id = member_id
                    break
            
            if other_member_id:
                other_member_info = await self.get_user_online_info(other_member_id)
                await self.send(text_data=json.dumps({
                    'type': 'online_status',
                    'is_personal_chat': True,
                    'is_online': other_member_info['is_online'],
                    'last_seen': other_member_info['last_seen']
                }))
        else:
            # Для группового чата показываем количество онлайн участников
            online_count = await self.get_online_members_count(self.chat_id)
            total_members = len(chat_info['members'])
            
            await self.send(text_data=json.dumps({
                'type': 'online_status',
                'is_personal_chat': False,
                'online_count': online_count,
                'total_members': total_members
            }))

    async def broadcast_online_status_update(self):
        """Отправляем обновление онлайн статуса всем участникам чата"""
        chat_info = await self.get_chat_info(self.chat_id)
        
        if chat_info['is_personal']:
            # Для персонального чата отправляем статус каждому участнику
            for member_id in chat_info['members']:
                other_member_id = None
                for mid in chat_info['members']:
                    if mid != member_id:
                        other_member_id = mid
                        break
                
                if other_member_id:
                    other_member_info = await self.get_user_online_info(other_member_id)
                    await self.channel_layer.group_send(
                        f'user_{member_id}',
                        {
                            'type': 'online_status_update',
                            'is_personal_chat': True,
                            'is_online': other_member_info['is_online'],
                            'last_seen': other_member_info['last_seen']
                        }
                    )
        else:
            # Для группового чата отправляем количество онлайн участников
            online_count = await self.get_online_members_count(self.chat_id)
            total_members = len(chat_info['members'])
            
            for member_id in chat_info['members']:
                await self.channel_layer.group_send(
                    f'user_{member_id}',
                    {
                        'type': 'online_status_update',
                        'is_personal_chat': False,
                        'online_count': online_count,
                        'total_members': total_members
                    }
                )

    @database_sync_to_async
    def update_user_online_status(self, is_online):
        """Обновляем онлайн статус пользователя в кэше"""
        user_id = self.scope["user"].id
        cache_key_online = f'user_online_{user_id}'
        cache_key_last_seen = f'user_last_seen_{user_id}'
        
        if is_online:
            # Устанавливаем пользователя как онлайн на 5 минут
            cache.set(cache_key_online, True, 300)  # 5 минут
            # Удаляем last_seen когда пользователь онлайн
            cache.delete(cache_key_last_seen)
        else:
            # Удаляем онлайн статус и устанавливаем время последнего посещения
            cache.delete(cache_key_online)
            cache.set(cache_key_last_seen, timezone.now().isoformat(), 86400)  # 24 часа

    @database_sync_to_async
    def get_user_online_info(self, user_id):
        """Получаем информацию об онлайн статусе пользователя из кэша"""
        cache_key_online = f'user_online_{user_id}'
        cache_key_last_seen = f'user_last_seen_{user_id}'
        
        is_online = cache.get(cache_key_online, False)
        last_seen_str = cache.get(cache_key_last_seen)
        last_seen_text = None
        
        if not is_online and last_seen_str:
            try:
                last_seen = timezone.datetime.fromisoformat(last_seen_str)
                if timezone.is_naive(last_seen):
                    last_seen = timezone.make_aware(last_seen)
                
                now = timezone.now()
                time_diff = now - last_seen
                
                if time_diff.days > 0:
                    last_seen_text = f"{time_diff.days} дн. тому"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    last_seen_text = f"{hours} год. тому"
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    last_seen_text = f"{minutes} хв. тому"
                else:
                    last_seen_text = "щойно"
            except:
                last_seen_text = None
        
        return {
            'is_online': is_online,
            'last_seen': last_seen_text
        }

    @database_sync_to_async
    def get_online_members_count(self, chat_id):
        """Получаем количество онлайн участников в групповом чате из кэша"""
        try:
            chat = ChatGroup.objects.get(id=chat_id)
            online_count = 0
            
            for member in chat.members.all():
                cache_key = f'user_online_{member.user.id}'
                if cache.get(cache_key, False):
                    online_count += 1
            
            return online_count
        except ChatGroup.DoesNotExist:
            return 0

    @database_sync_to_async
    def check_chat_access(self):
        try:
            user_profile = Profile.objects.get(user=self.scope["user"])
            chat = ChatGroup.objects.get(id=self.chat_id)
            return chat.members.filter(id=user_profile.id).exists()
        except (ChatGroup.DoesNotExist, Profile.DoesNotExist):
            return False

    @database_sync_to_async
    def get_user_profile(self):
        try:
            return Profile.objects.get(user=self.scope["user"])
        except Profile.DoesNotExist:
            return None

    @database_sync_to_async
    def get_chat_info(self, chat_id):
        try:
            chat = ChatGroup.objects.get(id=chat_id)
            return {
                'name': chat.name,
                'members': [member.user.id for member in chat.members.all()],
                'is_personal': chat.is_personal_chat
            }
        except ChatGroup.DoesNotExist:
            return None

    @database_sync_to_async
    def get_chat_display_name(self, chat_id, user_id):
        """Получаем правильное название чата для конкретного пользователя"""
        try:
            chat = ChatGroup.objects.get(id=chat_id)
            user_profile = Profile.objects.get(user_id=user_id)
            
            if chat.is_personal_chat:
                # Для персонального чата возвращаем имя собеседника
                other_member = chat.members.exclude(id=user_profile.id).first()
                if other_member:
                    return other_member.user.get_full_name() or other_member.user.username
                return chat.name
            else:
                # Для группового чата возвращаем название группы
                return chat.name
        except (ChatGroup.DoesNotExist, Profile.DoesNotExist):
            return "Unknown Chat"

    @database_sync_to_async
    def get_author_info(self, author_id):
        try:
            from user.models import Avatar
            author = Profile.objects.get(id=author_id)
            # Получаем активную аватарку
            avatar = Avatar.objects.filter(profile=author, active=True).first()
            avatar_url = avatar.image.url if avatar else '/static/img/avatarka.png'
            
            return {
                'name': author.user.get_full_name() or author.user.username,
                'avatar': avatar_url
            }
        except Profile.DoesNotExist:
            return {'name': 'Unknown', 'avatar': '/static/img/avatarka.png'}

    @database_sync_to_async
    def save_message(self, author_id, chat_id, message):
        try:
            author = Profile.objects.get(id=author_id)
            chat = ChatGroup.objects.get(id=chat_id)
            return ChatMessage.objects.create(
                author=author,
                chat_group=chat,
                content=message
            )
        except (Profile.DoesNotExist, ChatGroup.DoesNotExist):
            return None

    @database_sync_to_async
    def save_image_message(self, author_id, chat_id, caption, image_data):
        try:
            import uuid
            author = Profile.objects.get(id=author_id)
            chat = ChatGroup.objects.get(id=chat_id)
            
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            
            image_file = ContentFile(
                base64.b64decode(imgstr), 
                name=f'{uuid.uuid4()}.{ext}'
            )
            
            return ChatMessage.objects.create(
                author=author,
                chat_group=chat,
                content=caption,
                attached_image=image_file
            )
        except (Profile.DoesNotExist, ChatGroup.DoesNotExist, Exception):
            return None
