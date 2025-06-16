from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.ChatPageViews.as_view(), name = 'chats'),
    # path('send/<int:chat_id>/', views.SendMessageView.as_view(), name='send_message'),
]