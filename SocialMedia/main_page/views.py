from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreatePublicationsForm
from .models import Post, Tag, Image, Link
from django.contrib.auth.decorators import login_required
from .forms import UserProfileUpdateForm
from .models import Profile
from user.models import Avatar
from chats.models import ChatGroup, ChatMessage
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.models import User
from datetime import date

@require_POST
def add_tag(request):
    tag = request.POST.get('tag', '').strip()
    
    if tag:
        tag_object, created = Tag.objects.get_or_create(name=tag)
        if created:
            return JsonResponse({
                'status': 'success',
                'tag': tag_object.name,
                'id': tag_object.id,
                'created': created
            })
        else:
            return JsonResponse({
                'status': 'success',
                'tag': tag_object.name,
                'id': tag_object.id,
                'created': created
            })
    else:
        return JsonResponse({"status": "error", "message": "Порожній тег"})

@login_required
def render_main_page(request):
    user = request.user

    # Проверяем, есть ли у пользователя профиль
    try:
        user_profile = user.profile
        show_modal = False
    except Profile.DoesNotExist:
        user_profile = None
        show_modal = True

    if request.method == 'POST':
        # Обработка создания профиля
        if request.POST.get('force_update_profile') == '1':
            profile_form = UserProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                # Обновляем данные пользователя
                user.first_name = profile_form.cleaned_data['first_name']
                user.last_name = profile_form.cleaned_data['last_name']
                user.username = profile_form.cleaned_data['username']
                user.save()
                
                # Создаем профиль пользователя
                Profile.objects.create(
                    user=user,
                    date_of_birth=date.today()  # Устанавливаем текущую дату как временную
                )
                
                return redirect('main_page')
            else:
                return render(request, 'main_page/main_page.html', {
                    "user": user,
                    "form": CreatePublicationsForm(),
                    "publications": [],
                    "user_publications_count": 0,
                    "show_additional_info_modal": True,
                    "profile_form": profile_form,
                    "user_chats": [],
                })
        
        # Обработка создания публикации (только если есть профиль)
        elif user_profile:
            form = CreatePublicationsForm(request.POST, request.FILES)
            if form.is_valid():
                publication = form.save(commit=False)
                publication.author = user_profile
                publication.save()

                selected_tags = request.POST.get('selected_tags', '')
                tag_ids = [int(tid) for tid in selected_tags.split(',') if tid.isdigit()]
                if tag_ids:
                    publication.tags.set(tag_ids)
                else:
                    publication.tags.clear()

                uploaded_files = request.FILES.getlist('images')
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        image = Image.objects.create(filename=uploaded_file.name, file=uploaded_file)
                        publication.images.add(image)
                all_urls = []
                url_from_form = request.POST.get('url')
                if url_from_form and url_from_form.strip():
                    all_urls.append(url_from_form.strip())

                extra_urls = request.POST.getlist('extra_urls')
                all_urls.extend([url.strip() for url in extra_urls if url.strip()])

                for url in all_urls:
                    Link.objects.create(post=publication, url=url)

                return redirect('main_page')

    # Если нет профиля, показываем модальное окно
    if not user_profile:
        profile_form = UserProfileUpdateForm(instance=user)
        return render(request, 'main_page/main_page.html', {
            "user": user,
            "form": CreatePublicationsForm(),
            "publications": [],
            "user_publications_count": 0,
            "show_additional_info_modal": True,
            "profile_form": profile_form,
            "user_chats": [],
        })

    # Обычная логика для пользователей с профилем
    form = CreatePublicationsForm()
    user_publications_count = Post.objects.filter(author=user_profile).count()
    publications = Post.objects.all().prefetch_related('tags', 'images', 'link_set').order_by('-id')
    
    user_chats = ChatGroup.objects.filter(
        members=user_profile
    ).distinct().order_by('-id')[:3]
    
    chats_data = []
    for chat in user_chats:
        last_message = ChatMessage.objects.filter(chat_group=chat).order_by('-sent_at').first()
        
        if chat.is_personal_chat:
            other_member = chat.members.exclude(id=user_profile.id).first()
            chat_name = other_member.user.get_full_name() or other_member.user.username if other_member else chat.name
            avatar = other_member.avatar_set.filter(active = True).first() if other_member else None
            chat_avatar = avatar.image.url if avatar else '/static/img/avatarka.png'
        else:
            chat_name = chat.name
            chat_avatar = chat.avatar.url if chat.avatar else '/static/img/avatarka.png'
        
        chats_data.append({
            'id': chat.id,
            'name': chat_name,
            'avatar': chat_avatar,
            'last_message': last_message.content if last_message else 'Немає повідомлень',
            'last_message_time': last_message.sent_at.strftime('%H:%M') if last_message else '',
            'last_message_date': last_message.sent_at.strftime('%d.%m.%Y') if last_message else '',
            'is_today': last_message.sent_at.date() == user.date_joined.date() if last_message else False
        })

    return render(request, 'main_page/main_page.html', {
        "user": user,
        "form": form,
        "publications": publications,
        "user_publications_count": user_publications_count,
        "show_additional_info_modal": False,
        "profile_form": UserProfileUpdateForm(instance=user),
        "user_chats": chats_data,
    })
