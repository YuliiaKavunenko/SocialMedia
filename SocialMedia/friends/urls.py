from django.urls import path
from . import views

urlpatterns = [
    path('', views.FriendsPageViews.as_view(), name = 'friends' ),
    path('all/', views.AllFriendsPageViews.as_view(), name = 'all_friends'),
    path('recommendations/', views.RecommendationsPageViews.as_view(), name = 'recommendations'),
    path('requests/', views.RequestsPageViews.as_view(), name = 'requests'),
]