from django.shortcuts import render
from django.views import View
from main_page.models import Profile
from user.models import Avatar, Friendship
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json



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
