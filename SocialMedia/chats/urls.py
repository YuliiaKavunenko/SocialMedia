from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.ChatPageViews.as_view(), name = 'chats'),
    # path('chats/<int:chat_id>/', views.PersonalChatView.as_view(), name = 'chat_detail'),
]