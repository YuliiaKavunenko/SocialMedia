from django.urls import path
from . import views

urlpatterns = [
    path('', views.FriendsPageViews.as_view(), name = 'friends' ),
]