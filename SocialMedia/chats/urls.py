from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.chat_view, name = 'chats'),
    path('delete/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('get-users/', views.get_users, name='get_users'),
    path('create-group/', views.create_group, name='create_group'),
    path('get-group-data/<int:chat_id>/', views.get_group_data, name='get_group_data'),
    path('update-group/<int:chat_id>/', views.update_group, name='update_group'),
    path('add-members/<int:chat_id>/', views.add_members, name='add_members'),
    path('remove-member/<int:chat_id>/', views.remove_member, name='remove_member'),
    path('leave-group/<int:chat_id>/', views.leave_group, name='leave_group'),
    # path('chats/', views.ChatPageViews.as_view(), name = 'chats'),
    # path('send/<int:chat_id>/', views.SendMessageView.as_view(), name='send_message'),
]