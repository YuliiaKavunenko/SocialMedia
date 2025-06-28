from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from main_page.models import Post, Tag, Image, Link
from user.models import Avatar
from user.models import Friendship
from main_page.forms import CreatePublicationsForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import models

@login_required
def edit_publication(request, pub_id):
    publication = get_object_or_404(Post, id=pub_id, author__user=request.user)

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = request.user.profile
            
            # Получаем выбранные теги для установки темі при редактировании
            selected_tags = request.POST.get('selected_tags', '')
            tag_ids = [int(tid) for tid in selected_tags.split(',') if tid.isdigit()]
            
            # Устанавливаем тему как последний выбранный тег
            if tag_ids:
                last_tag = Tag.objects.filter(id=tag_ids[-1]).first()
                if last_tag:
                    publication.topic = last_tag.name
            else:
                publication.topic = ''
            
            publication.save()

            # Обработка тегов для редактирования
            if tag_ids:
                publication.tags.set(tag_ids)
            else:
                publication.tags.clear()

            # Обработка удаления существующих изображений
            images_to_delete = request.POST.get('images_to_delete', '')
            if images_to_delete:
                image_ids = [int(img_id) for img_id in images_to_delete.split(',') if img_id.isdigit()]
                for image_id in image_ids:
                    try:
                        image = Image.objects.get(id=image_id)
                        publication.images.remove(image)
                        image.delete()  # Удаляем изображение полностью
                    except Image.DoesNotExist:
                        pass

            # Обработка множественных изображений для редактирования
            uploaded_files = request.FILES.getlist('images')
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    image = Image.objects.create(filename=uploaded_file.name, file=uploaded_file)
                    publication.images.add(image)

            # Обработка ссылок для редактирования
            # Удаляем старые ссылки
            publication.link_set.all().delete()
            
            # Добавляем новые ссылки
            all_urls = []
            url_from_form = request.POST.get('url')
            if url_from_form and url_from_form.strip():
                all_urls.append(url_from_form.strip())

            extra_urls = request.POST.getlist('extra_urls')
            all_urls.extend([url.strip() for url in extra_urls if url.strip()])

            for url in all_urls:
                Link.objects.create(post=publication, url=url)

            return redirect('my_publications')
    else:
        form = CreatePublicationsForm(instance=publication)

    return render(
        request,
        "my_publications/my_publications.html",
        {
            "user": request.user,
            "form": form,
            "publication": publication,
        }
    )

@login_required
def delete_publication(request, pub_id):
    publication = get_object_or_404(Post, id=pub_id, author__user=request.user)  # проверка автора

    if request.method == "POST":
        publication.delete()
        return redirect('my_publications')
    

@login_required
def render_my_publications_page(request):
    user = request.user
    form = CreatePublicationsForm()

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES)

        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = user.profile
            
            # Получаем выбранные теги для установки topic
            selected_tags = request.POST.get('selected_tags', '')
            tag_ids = [int(tid) for tid in selected_tags.split(',') if tid.isdigit()]
            
            # Устанавливаем topic как последний выбранный тег
            if tag_ids:
                last_tag = Tag.objects.filter(id=tag_ids[-1]).first()
                if last_tag:
                    publication.topic = last_tag.name
            else:
                publication.topic = ''
            
            publication.save()

            # Теги
            if tag_ids:
                publication.tags.set(tag_ids)
            else:
                publication.tags.clear()  # щоб не лишились старі теги

            # Множественные изображения
            uploaded_files = request.FILES.getlist('images')
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    image = Image.objects.create(filename=uploaded_file.name, file=uploaded_file)
                    publication.images.add(image)

            # Посилання
            all_urls = []
            url_from_form = request.POST.get('url')
            if url_from_form and url_from_form.strip():
                all_urls.append(url_from_form.strip())

            extra_urls = request.POST.getlist('extra_urls')
            all_urls.extend([url.strip() for url in extra_urls if url.strip()])

            for url in all_urls:
                Link.objects.create(post=publication, url=url)

            return redirect('my_publications')

    publications = Post.objects.filter(author__user=user).prefetch_related('tags', 'images', 'link_set').order_by('-id')

    # Подсчет публикаций пользователя для отображения в профиле
    user_posts_count = publications.count()

    # Получаем количество друзей
    user_friends_count = Friendship.objects.filter(
        models.Q(profile1=user.profile, accepted=True) | 
        models.Q(profile2=user.profile, accepted=True)
    ).count()

    # Получаем количество входящих запросов на дружбу
    user_friend_requests_count = Friendship.objects.filter(
        profile2=user.profile, 
        accepted=False
    ).count()

    # Подписчиков пока 0
    user_followers_count = 0
    
    # Получаем аватар пользователя
    user_avatar = user.profile.avatar_set.filter(active=True).first() if hasattr(user, 'profile') else None
    
    # Добавляем аватары авторов к публикациям
    publications_with_avatars = []
    for pub in publications:
        pub_data = {
            'publication': pub,
            'author_avatar': pub.author.avatar_set.filter(active=True).first() if pub.author else None
        }
        publications_with_avatars.append(pub_data)

    return render(request, "my_publications/my_publications.html", {
        "user": user,
        "form": form,
        "publications": publications,
        "publications_with_avatars": publications_with_avatars,
        "user_posts_count": user_posts_count,
        "user_friends_count": user_friends_count,
        "user_followers_count": user_followers_count,
        "user_friend_requests_count": user_friend_requests_count,
        "user_avatar": user_avatar,
    })


@require_POST
def add_tag(request):
    tag = request.POST.get('tag', '').strip()
    
    if tag:
        tag_object, created = Tag.objects.get_or_create(name = tag)
        if created:
            return JsonResponse({
                'status' : 'success',
                'tag' : tag_object.name,
                'id' : tag_object.id,
                'created' : created
            })
        else:
            return JsonResponse({
                'status' : 'success',
                'tag' : tag_object.name,
                'id' : tag_object.id,
                'created' : created
            })
    else:
        return JsonResponse({"status": "error", "message": "Порожній тег"})
