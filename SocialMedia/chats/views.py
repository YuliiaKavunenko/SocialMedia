from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatGroup, ChatMessage
from user.models import Profile
from datetime import timedelta
from django.utils import timezone

@login_required
def chat_view(request):
    user_profile = request.user.profile
    
    # Получаем все чаты пользователя
    personal_chats = ChatGroup.objects.filter(
        members = user_profile, 
        is_personal_chat = True
    ).distinct().order_by('-id')
    
    group_chats = ChatGroup.objects.filter(
        members=user_profile, 
        is_personal_chat = False
    ).distinct().order_by('-id')
    
    # Получаем контакты
    contacts = Profile.objects.exclude(id = user_profile.id)
    
    active_chat = None
    messages = []
    grouped_messages = []
    
    # Если указан chat_id, получаем активный чат
    chat_id = request.GET.get('chat_id')
    if chat_id:
        try:
            active_chat = ChatGroup.objects.get(
                id = chat_id, 
                members = user_profile
            )
            messages = ChatMessage.objects.filter(
                chat_group=active_chat
            ).order_by('sent_at')
            
            # Группируем сообщения по датам
            current_date = None
            for message in messages:
                message_date = message.sent_at.date()
                if current_date != message_date:
                    grouped_messages.append({
                        'type': 'date',
                        'date': message_date
                    })
                    current_date = message_date
                grouped_messages.append({
                    'type': 'message',
                    'message': message,
                    'adjusted_sent_at': message.sent_at + timedelta(hours = 3)
                })
        except ChatGroup.DoesNotExist:
            pass
    
    # Если указан contact_id — создаем или находим персональный чат
    contact_id = request.GET.get('contact_id')
    if contact_id:
        try:
            contact = get_object_or_404(Profile, id=contact_id)
            
            # Ищем существующий чат между пользователями
            existing_chats = ChatGroup.objects.filter(
                is_personal_chat=True, 
                members=user_profile
            )
            
            for chat in existing_chats:
                if chat.members.filter(id=contact.id).exists():
                    active_chat = chat
                    break
            
            # Если чат не найден, создаем новый
            if not active_chat:
                # Имя чата по собеседнику
                chat_name = contact.user.get_full_name() or contact.user.username
                active_chat = ChatGroup.objects.create(
                    name=chat_name,
                    is_personal_chat=True,
                    admin=user_profile
                )
                active_chat.members.add(user_profile, contact)
                
                # Обновляем список персональных чатов
                personal_chats = ChatGroup.objects.filter(
                    members=user_profile, 
                    is_personal_chat=True
                ).distinct().order_by('-id')
            
            # Получаем сообщения для активного чата
            messages = ChatMessage.objects.filter(
                chat_group=active_chat
            ).order_by('sent_at')
            
            # Группируем сообщения по датам
            current_date = None
            for message in messages:
                message_date = message.sent_at.date()
                if current_date != message_date:
                    grouped_messages.append({
                        'type': 'date',
                        'date': message_date
                    })
                    current_date = message_date
                grouped_messages.append({
                    'type': 'message',
                    'message': message
                })
                
        except Profile.DoesNotExist:
            pass
    
    # Устанавливаем правильные названия для персональных чатов
    for chat in personal_chats:
        if chat.is_personal_chat:
            # Находим собеседника (не текущего пользователя)
            other_member = chat.members.exclude(id=user_profile.id).first()
            if other_member:
                chat.display_name = other_member.user.get_full_name() or other_member.user.username
            else:
                chat.display_name = chat.name
        else:
            chat.display_name = chat.name
            
        last_msg = chat.chatmessage_set.last()
        if last_msg:
            chat.last_message = last_msg
            chat.last_message_time = last_msg.sent_at + timedelta(hours = 3)

    for chat in group_chats:
        chat.display_name = chat.name
        last_msg = chat.chatmessage_set.last()
        if last_msg:
            chat.last_message = last_msg
            chat.last_message_time = last_msg.sent_at + timedelta(hours = 3)

    # Устанавливаем правильное название для активного чата
    if active_chat and active_chat.is_personal_chat:
        other_member = active_chat.members.exclude(id=user_profile.id).first()
        if other_member:
            active_chat.display_name = other_member.user.get_full_name() or other_member.user.username
        else:
            active_chat.display_name = active_chat.name
    elif active_chat:
        active_chat.display_name = active_chat.name
    
    context = {
        'personal_chats': personal_chats,
        'group_chats': group_chats,
        'contacts': contacts,
        'active_chat': active_chat,
        'messages': messages,
        'grouped_messages': grouped_messages,
    }
    
    return render(request, 'chats/chats.html', context)

@login_required
@require_POST
def delete_chat(request, chat_id):
    try:
        user_profile = request.user.profile
        
        # Получаем чат и проверяем права доступа
        chat = get_object_or_404(ChatGroup, id=chat_id, members=user_profile)
        
        # Проверяем, является ли пользователь администратором чата или это персональный чат
        if chat.admin == user_profile or chat.is_personal_chat:
            # Удаляем все сообщения чата
            ChatMessage.objects.filter(chat_group=chat).delete()
            
            # Удаляем сам чат
            chat.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Чат успішно видалений'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'У вас немає прав для видалення цього чату'
            })
            
    except ChatGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Чат не знайдено'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при видаленні чату'
        })

@login_required
def get_users(request):
    """Получение списка пользователей для создания группы"""
    try:
        user_profile = request.user.profile
        
        # Получаем всех пользователей кроме текущего
        users = Profile.objects.exclude(id=user_profile.id).select_related('user')
        
        users_data = []
        for profile in users:
            # Получаем активную аватарку пользователя
            avatar = profile.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None
            
            users_data.append({
                'id': profile.id,
                'name': profile.user.get_full_name() or profile.user.username,
                'username': profile.user.username,
                'avatar': avatar_url
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при завантаженні користувачів'
        })

@login_required
@require_POST
def create_group(request):
    """Создание новой группы"""
    try:
        user_profile = request.user.profile
        
        # Получаем данные из форм
        group_name = request.POST.get('name', '').strip()
        members_json = request.POST.get('members', '[]')
        avatar_file = request.FILES.get('avatar')
        
        # Валидация
        if not group_name:
            return JsonResponse({
                'success': False,
                'error': 'Назва групи обов\'язкова'
            })
        
        try:
            member_ids = json.loads(members_json)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Некоректні дані учасників'
            })
        
        if not member_ids:
            return JsonResponse({
                'success': False,
                'error': 'Оберіть хоча б одного учасника'
            })
        
        # Создаем группу
        group = ChatGroup.objects.create(
            name=group_name,
            is_personal_chat=False,
            admin=user_profile
        )
        
        # Добавляем аватар если есть
        if avatar_file:
            group.avatar = avatar_file
            group.save()
        
        # Добавляем создателя группы
        group.members.add(user_profile)
        
        # Добавляем выбранных участников
        for member_id in member_ids:
            try:
                member = Profile.objects.get(id=member_id)
                group.members.add(member)
            except Profile.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': 'Група успішно створена',
            'chat_id': group.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при створенні групи'
        })

@login_required
def get_group_data(request, chat_id):
    """Получение данных группы для редактирования"""
    try:
        user_profile = request.user.profile
        
        # Получаем группу и проверяем права доступа
        group = get_object_or_404(ChatGroup, id=chat_id, members=user_profile)
        
        # Проверяем, является ли пользователь администратором
        if group.admin != user_profile:
            return JsonResponse({
                'success': False,
                'error': 'У вас немає прав для редагування цієї групи'
            })
        
        # Получаем данные участников
        members_data = []
        for member in group.members.all():
            avatar = member.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None
            
            members_data.append({
                'id': member.id,
                'name': member.user.get_full_name() or member.user.username,
                'username': member.user.username,
                'avatar': avatar_url
            })
        
        group_data = {
            'id': group.id,
            'name': group.name,
            'avatar': group.avatar.url if group.avatar else None,
            'admin_id': group.admin.id,
            'members': members_data
        }
        
        return JsonResponse({
            'success': True,
            'group': group_data
        })
        
    except ChatGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Група не знайдена'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при завантаженні даних групи'
        })

@login_required
@require_POST
def update_group(request, chat_id):
    """Обновление данных группы"""
    try:
        user_profile = request.user.profile
        
        # Получаем группу и проверяем права доступа
        group = get_object_or_404(ChatGroup, id=chat_id, members=user_profile)
        
        # Проверяем, является ли пользователь администратором
        if group.admin != user_profile:
            return JsonResponse({
                'success': False,
                'error': 'У вас немає прав для редагування цієї групи'
            })
        
        # Получаем данные из формы
        group_name = request.POST.get('name', '').strip()
        avatar_file = request.FILES.get('avatar')
        
        # Валидация
        if not group_name:
            return JsonResponse({
                'success': False,
                'error': 'Назва групи обов\'язкова'
            })
        
        # Обновляем данные группы
        group.name = group_name
        
        if avatar_file:
            group.avatar = avatar_file
        
        group.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Група успішно оновлена'
        })
        
    except ChatGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Група не знайдена'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при оновленні групи'
        })

@login_required
@require_POST
def add_members(request, chat_id):
    """Добавление участников в группу"""
    try:
        user_profile = request.user.profile
        
        # Получаем группу и проверяем права доступа
        group = get_object_or_404(ChatGroup, id=chat_id, members=user_profile)
        
        # Проверяем, является ли пользователь администратором
        if group.admin != user_profile:
            return JsonResponse({
                'success': False,
                'error': 'У вас немає прав для додавання учасників'
            })
        
        # Получаем данные из запроса
        data = json.loads(request.body)
        member_ids = data.get('member_ids', [])
        
        if not member_ids:
            return JsonResponse({
                'success': False,
                'error': 'Не вибрано учасників для додавання'
            })
        
        # Добавляем участников
        added_count = 0
        for member_id in member_ids:
            try:
                member = Profile.objects.get(id=member_id)
                if not group.members.filter(id=member_id).exists():
                    group.members.add(member)
                    added_count += 1
            except Profile.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Додано {added_count} учасників'
        })
        
    except ChatGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Група не знайдена'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при додаванні учасників'
        })

@login_required
@require_POST
def remove_member(request, chat_id):
    """Удаление участника из группы"""
    try:
        user_profile = request.user.profile
        
        # Получаем группу и проверяем права доступа
        group = get_object_or_404(ChatGroup, id=chat_id, members=user_profile)
        
        # Проверяем, является ли пользователь администратором
        if group.admin != user_profile:
            return JsonResponse({
                'success': False,
                'error': 'У вас немає прав для видалення учасників'
            })
        
        # Получаем данные из запроса
        data = json.loads(request.body)
        member_id = data.get('member_id')
        
        if not member_id:
            return JsonResponse({
                'success': False,
                'error': 'Не вказано учасника для видалення'
            })
        
        # Проверяем, что не пытаемся удалить администратора
        if member_id == user_profile.id:
            return JsonResponse({
                'success': False,
                'error': 'Адміністратор не може видалити себе з групи'
            })
        
        # Удаляем участника
        try:
            member = Profile.objects.get(id=member_id)
            group.members.remove(member)
            
            return JsonResponse({
                'success': True,
                'message': 'Учасника видалено з групи'
            })
        except Profile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Учасник не знайдений'
            })
        
    except ChatGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Група не знайдена'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при видаленні учасника'
        })

@login_required
@require_POST
def leave_group(request, chat_id):
    """Выход пользователя из группы"""
    try:
        user_profile = request.user.profile
        
        # Получаем группу и проверяем права доступа
        group = get_object_or_404(ChatGroup, id=chat_id, members=user_profile)
        
        # Проверяем, что это не персональный чат
        if group.is_personal_chat:
            return JsonResponse({
                'success': False,
                'error': 'Неможливо покинути персональний чат'
            })
        
        # Если пользователь администратор, нужно передать права или удалить группу
        if group.admin == user_profile:
            # Если в группе есть другие участники, передаем права первому из них
            other_members = group.members.exclude(id=user_profile.id)
            if other_members.exists():
                new_admin = other_members.first()
                group.admin = new_admin
                group.save()
            else:
                # Если других участников нет, удаляем группу
                ChatMessage.objects.filter(chat_group=group).delete()
                group.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Ви покинули групу. Група була видалена.'
                })
        
        # Удаляем пользователя из группы
        group.members.remove(user_profile)
        
        return JsonResponse({
            'success': True,
            'message': 'Ви покинули групу'
        })
        
    except ChatGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Група не знайдена'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Помилка при виході з групи'
        })

# class SendMessageView(LoginRequiredMixin, View):
#     def post(self, request, chat_id):
#         chat = get_object_or_404(ChatGroup, id = chat_id)
#         content = request.POST.get('content')
#         image = request.FILES.get('attached_image')
#         profile = request.user.profile

#         if content or image:
#             ChatMessage.objects.create(
#                 content = content,
#                 author = profile,
#                 chat_group = chat,
#                 attached_image = image
#             )

#         return redirect(f'/chats/?chat_id = {chat.id}')
