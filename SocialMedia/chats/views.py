from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from user.models import Profile
from .models import ChatGroup, ChatMessage

class ChatPageViews(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user.profile

        # Усі користувачі для списку контактів
        contacts = Profile.objects.exclude(id=user.id)

        # Усі чати, де є поточний користувач
        all_chats = ChatGroup.objects.filter(members=user)

        # Поділ на особисті та групові
        personal_chats = all_chats.filter(is_personal_chat=True)
        group_chats = all_chats.filter(is_personal_chat=False)

        # Якщо передано chat_id
        active_chat_id = request.GET.get('chat_id')
        active_chat = None

        if active_chat_id:
            active_chat = ChatGroup.objects.filter(id = active_chat_id, members = user).first()

        # Якщо передано contact_id — шукаємо або створюємо особистий чат
        contact_id = request.GET.get('contact_id')
        if contact_id:
            contact = get_object_or_404(Profile, id=contact_id)

            # Чи існує чат між user та contact
            existing_chats = ChatGroup.objects.filter(is_personal_chat = True, members = user)
            for chat in existing_chats:
                if chat.members.filter(id=contact.id).exists():
                    active_chat = chat
                    break

            # Якщо не існує, то створюємо новий персональний чат
            if not active_chat:
                new_chat = ChatGroup.objects.create(
                    name = f"{user.user.username} & {contact.user.username}",
                    is_personal_chat = True,
                    admin = user
                )
                new_chat.members.add(user, contact)
                active_chat = new_chat

        # Повідомлення для активного чату
        if active_chat:
            messages = ChatMessage.objects.filter(chat_group = active_chat).order_by('sent_at') 
        else:
            messages = None

        return render(request, 'chats/chats.html', {
            'contacts': contacts,
            'personal_chats': personal_chats,
            'group_chats': group_chats,
            'active_chat': active_chat,
            'messages': messages
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
