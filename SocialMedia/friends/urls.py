from django.urls import path
from . import views

urlpatterns = [
    path('', views.FriendsPageViews.as_view(), name = 'friends' ),
    path('all/', views.AllFriendsPageViews.as_view(), name = 'all_friends'),
    path('recommendations/', views.RecommendationsPageViews.as_view(), name = 'recommendations'),
    path('requests/', views.RequestsPageViews.as_view(), name = 'requests'),
    path('accept-request/', views.AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('decline-request/', views.DeclineFriendRequestView.as_view(), name='decline_friend_request'),
    path('send-request/', views.SendFriendRequestView.as_view(), name='send_friend_request'),
    path('remove-friend/', views.RemoveFriendView.as_view(), name='remove_friend'),
    path('remove-recommendation/', views.RemoveRecommendationView.as_view(), name='remove_recommendation'),
    path('create-personal-chat/', views.CreateOrFindPersonalChatView.as_view(), name='create_personal_chat'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
]
