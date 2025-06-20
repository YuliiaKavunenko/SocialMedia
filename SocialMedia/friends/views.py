from django.shortcuts import render
from django.views import View
from main_page.models import Profile
from user.models import Avatar, Friendship
from django.contrib.auth.models import User
from django.db.models import Q
# Create your views here.
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

        # Рекомендації
        users = User.objects.all().exclude(id=request.user.id)
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
        users = User.objects.all().exclude(id = request.user.id)  # не показувати себе

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
