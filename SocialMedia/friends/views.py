from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from main_page.models import Profile
from user.models import Avatar, Friendship
from chats.models import ChatGroup, ChatMessage
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from main_page.models import Post, Album

class FriendsPageViews(View):
    template_name = 'friends/friends.html'

    def get(self, request):
        try:
            current_profile = request.user.profile
        except Profile.DoesNotExist:
            return render(request, self.template_name, {
                'friends': [],
                'friend_requests': [],
                'recommended_users': []
            })

        # Друзі
        friendships = Friendship.objects.filter(
            accepted=True
        ).filter(
            Q(profile1=current_profile) | Q(profile2=current_profile)
        )

        friends = []
        for friendship in friendships:
            friend_profile = friendship.profile2 if friendship.profile1 == current_profile else friendship.profile1
            user = friend_profile.user
            avatar = friend_profile.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None

            friends.append({
                'username': user.username,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': avatar_url
            })

        # Вхідні запити
        friend_requests = Friendship.objects.filter(
            profile2=current_profile,
            accepted=False
        )

        requested_users = []
        for request_obj in friend_requests:
            user = request_obj.profile1.user
            avatar = request_obj.profile1.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None

            requested_users.append({
                'username': user.username,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': avatar_url
            })

        # Рекомендації - исключаем уже отправленные запросы и друзей
        users = User.objects.all().exclude(id=request.user.id)
        
        # Получаем ID пользователей, с которыми уже есть связь
        existing_connections = Friendship.objects.filter(
            Q(profile1=current_profile) | Q(profile2=current_profile)
        ).values_list('profile1__user__id', 'profile2__user__id')
        
        connected_user_ids = set()
        for conn in existing_connections:
            connected_user_ids.update(conn)
        connected_user_ids.discard(request.user.id)
        
        # Исключаем пользователей с существующими связями
        users = users.exclude(id__in=connected_user_ids)
        
        recommended_users = []
        for user in users:
            try:
                profile = user.profile
                avatar = profile.avatar_set.filter(active=True).first()
                avatar_url = avatar.image.url if avatar else None
            except Profile.DoesNotExist:
                avatar_url = None

            recommended_users.append({
                'username': user.username,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': avatar_url
            })

        return render(request, self.template_name, {
            'friends': friends,
            'friend_requests': requested_users,
            'recommended_users': recommended_users
        })

class AllFriendsPageViews(View):
    template_name = 'friends/allfriends.html'

    def get(self, request):
        try:
            current_profile = request.user.profile
        except Profile.DoesNotExist:
            return render(request, self.template_name, {'friends': []})

        friendships = Friendship.objects.filter(
            accepted=True
        ).filter(
            Q(profile1 = current_profile) | Q(profile2 = current_profile)
        )

        friends = []

        for friendship in friendships:
            friend_profile = (
                friendship.profile2 if friendship.profile1 == current_profile else friendship.profile1
            )

            user = friend_profile.user
            avatar = friend_profile.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None

            friends.append({
                'username': user.username,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': avatar_url
            })

        return render(request, self.template_name, {'friends': friends})

class RecommendationsPageViews(View):
    template_name = 'friends/recommendations.html'

    def get(self, request):
        try:
            current_profile = request.user.profile
        except Profile.DoesNotExist:
            current_profile = None

        users = User.objects.all().exclude(id=request.user.id)
        
        if current_profile:
            # Исключаем пользователей с существующими связями
            existing_connections = Friendship.objects.filter(
                Q(profile1=current_profile) | Q(profile2=current_profile)
            ).values_list('profile1__user__id', 'profile2__user__id')
            
            connected_user_ids = set()
            for conn in existing_connections:
                connected_user_ids.update(conn)
            connected_user_ids.discard(request.user.id)
            
            users = users.exclude(id__in=connected_user_ids)

        recommended_users = []
        for user in users:
            try:
                profile = user.profile
                avatar = profile.avatar_set.filter(active=True).first()
                avatar_url = avatar.image.url if avatar else None
            except Profile.DoesNotExist:
                avatar_url = None

            recommended_users.append({
                'username': user.username,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': avatar_url
            })

        return render(request, self.template_name, {'recommended_users': recommended_users})

class RequestsPageViews(View):
    template_name = 'friends/requests.html'

    def get(self, request):
        try:
            current_profile = request.user.profile
        except Profile.DoesNotExist:
            return render(request, self.template_name, {'friend_requests': []})

        friend_requests = Friendship.objects.filter(
            profile2=current_profile,
            accepted=False
        )

        requested_users = []
        for request_obj in friend_requests:
            user = request_obj.profile1.user
            avatar = request_obj.profile1.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None

            requested_users.append({
                'username': user.username,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': avatar_url
            })

        return render(request, self.template_name, {'friend_requests': requested_users})

# Новый view для страницы пользователя
class UserProfileView(View):
    template_name = 'friends/friend_page.html'

    def get(self, request, username):
        try:
            user = get_object_or_404(User, username=username)
            profile = user.profile
            avatar = profile.avatar_set.filter(active=True).first()
            avatar_url = avatar.image.url if avatar else None
            
            # Получаем статистику пользователя
            posts_count = Post.objects.filter(author=profile).count()
            friends_count = Friendship.objects.filter(
                Q(profile1=profile, accepted=True) | Q(profile2=profile, accepted=True)
            ).count()
            followers_count = friends_count  # В данной модели читачи = друзья

            # Получаем посты пользователя
            user_posts = Post.objects.filter(author=profile).order_by('-id')
            posts_with_data = []
            for post in user_posts:
                post_author_avatar = post.author.avatar_set.filter(active=True).first()
                posts_with_data.append({
                    'post': post,
                    'author_avatar': post_author_avatar
                })

            # Получаем альбомы пользователя
            user_albums = Album.objects.filter(author=profile, shown=True).order_by('-created_at')
            albums_with_images = []
            for album in user_albums:
                # Получаем последние 2 изображения из альбома
                last_images = album.images.all().order_by('-uploaded_at')[:2]
                albums_with_images.append({
                    'album': album,
                    'last_images': last_images
                })
            
            # Проверяем отношения с текущим пользователем
            current_profile = request.user.profile
            friendship_status = None
            
            if current_profile != profile:
                friendship = Friendship.objects.filter(
                    Q(profile1=current_profile, profile2=profile) |
                    Q(profile1=profile, profile2=current_profile)
                ).first()
                
                if friendship:
                    if friendship.accepted:
                        friendship_status = 'friends'
                    elif friendship.profile1 == current_profile:
                        friendship_status = 'request_sent'
                    else:
                        friendship_status = 'request_received'
                else:
                    friendship_status = 'none'
            
            context = {
                'profile_user': user,
                'profile': profile,
                'avatar_url': avatar_url,
                'friendship_status': friendship_status,
                'is_own_profile': current_profile == profile,
                'posts_count': posts_count,
                'friends_count': friends_count,
                'followers_count': followers_count,
                'user_posts': posts_with_data,
                'user_albums': albums_with_images,
            }
            
            return render(request, self.template_name, context)
            
        except Profile.DoesNotExist:
            return render(request, self.template_name, {'error': 'Профиль не найден'})

@method_decorator(login_required, name='dispatch')
class AcceptFriendRequestView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required'})
            
            # Найти пользователя, который отправил запрос
            sender_user = User.objects.get(username=username)
            sender_profile = sender_user.profile
            current_profile = request.user.profile
            
            # Найти запрос на дружбу
            friendship = Friendship.objects.get(
                profile1=sender_profile,
                profile2=current_profile,
                accepted=False
            )
            
            # Принять запрос
            friendship.accepted = True
            friendship.save()
            
            return JsonResponse({'success': True, 'message': 'Запрос на дружбу принят'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})
        except Friendship.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Запрос на дружбу не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class DeclineFriendRequestView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required'})
            
            # Найти пользователя, который отправил запрос
            sender_user = User.objects.get(username=username)
            sender_profile = sender_user.profile
            current_profile = request.user.profile
            
            # Найти и удалить запрос на дружбу
            friendship = Friendship.objects.get(
                profile1=sender_profile,
                profile2=current_profile,
                accepted=False
            )
            friendship.delete()
            
            return JsonResponse({'success': True, 'message': 'Запрос на дружбу отклонен'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})
        except Friendship.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Запрос на дружбу не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class SendFriendRequestView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required'})
            
            # Найти пользователя, которому отправляем запрос
            target_user = User.objects.get(username=username)
            target_profile = target_user.profile
            current_profile = request.user.profile
            
            # Проверить, не отправлен ли уже запрос
            existing_request = Friendship.objects.filter(
                Q(profile1=current_profile, profile2=target_profile) |
                Q(profile1=target_profile, profile2=current_profile)
            ).first()
            
            if existing_request:
                if existing_request.accepted:
                    return JsonResponse({'success': False, 'error': 'Вы уже друзья'})
                else:
                    return JsonResponse({'success': False, 'error': 'Запрос уже отправлен'})
            
            # Создать новый запрос на дружбу
            Friendship.objects.create(
                profile1=current_profile,
                profile2=target_profile,
                accepted=False
            )
            
            return JsonResponse({'success': True, 'message': 'Запрос на дружбу отправлен'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class RemoveFriendView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required'})
            
            friend_user = User.objects.get(username=username)
            friend_profile = friend_user.profile
            current_profile = request.user.profile
            
            friendship = Friendship.objects.filter(
                Q(profile1=current_profile, profile2=friend_profile) |
                Q(profile1=friend_profile, profile2=current_profile),
                accepted=True
            ).first()
            
            if not friendship:
                return JsonResponse({'success': False, 'error': 'Дружба не найдена'})
            
            friendship.delete()
            
            return JsonResponse({'success': True, 'message': 'Друг удален'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class RemoveRecommendationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required'})

            return JsonResponse({'success': True, 'message': 'Рекомендация удалена'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Новый view для создания/поиска личного чата
@method_decorator(login_required, name='dispatch')
class CreateOrFindPersonalChatView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required'})
            
            # Найти пользователя для чата
            target_user = User.objects.get(username=username)
            target_profile = target_user.profile
            current_profile = request.user.profile
            
            # Проверить, существует ли уже личный чат между этими пользователями
            existing_chat = ChatGroup.objects.filter(
                is_personal_chat=True,
                members__in=[current_profile]
            ).filter(
                members__in=[target_profile]
            ).first()
            
            if existing_chat:
                # Чат уже существует, возвращаем его ID
                return JsonResponse({
                    'success': True, 
                    'chat_id': existing_chat.id,
                    'message': 'Переход в существующий чат'
                })
            else:
                # Создаем новый личный чат
                new_chat = ChatGroup.objects.create(
                    name=f"Чат между {current_profile.user.username} и {target_profile.user.username}",
                    is_personal_chat=True,
                    admin=current_profile
                )
                new_chat.members.add(current_profile, target_profile)
                
                return JsonResponse({
                    'success': True, 
                    'chat_id': new_chat.id,
                    'message': 'Создан новый чат'
                })
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
