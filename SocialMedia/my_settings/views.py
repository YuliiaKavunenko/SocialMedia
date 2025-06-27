import random
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import EditUserDataForm, EditUsernameForm, EditAlbumForm, CreateAlbumForm, EditPasswordForm
from main_page.models import Album, Image
from user.models import Avatar, Profile
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
import json

class SettingsPageViews(LoginRequiredMixin, TemplateView):
    template_name = 'my_settings/my_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['edit_user_data_form'] = EditUserDataForm(instance=user)
        context['edit_password_form'] = EditPasswordForm(user = user)
        context['edit_username_form'] = EditUsernameForm(instance=user)

        profile = Profile.objects.filter(user=user).first()
        birth_date = profile.date_of_birth.isoformat() if profile and profile.date_of_birth else None

        context['edit_user_data_form'] = EditUserDataForm(
            instance=user,
            initial={'birth_date': birth_date}
        )
        avatar = None
        if profile:
            avatar = Avatar.objects.filter(profile=profile, active=True).first()

        context['active_avatar'] = avatar

        # Добавляем обработку ошибок кода подтверждения
        if 'password_code_error' in self.request.session:
            context['password_code_error'] = self.request.session.pop('password_code_error')
            context['show_password_modal'] = True

        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user

        # Добавляем обработку подтверждения кода
        if 'action' in request.POST and request.POST['action'] == 'confirm_password_code':
            email = request.POST.get('email')
            session_key = f"password_verification_code_{email}"
            stored_code = request.session.get(session_key)
            
            # Собираем код из отдельных полей
            entered_code = ''
            for i in range(1, 7):
                code_part = request.POST.get(f'code{i}', '')
                entered_code += code_part
            
            if stored_code and entered_code == stored_code:
                # Код правильный - устанавливаем флаг верификации
                request.session['password_verified'] = True
                request.session.pop(session_key, None)  # Удаляем использованный код
                request.session.pop('show_password_modal', None)
                request.session.modified = True
                return redirect('settings')
            else:
                # Код неправильный
                request.session['password_code_error'] = 'Неправильний код підтвердження'
                request.session['show_password_modal'] = True
                request.session.modified = True
                return redirect('settings')

        if 'edit_password' in request.POST:
            # Проверяем, была ли верификация пароля
            if not request.session.get('password_verified', False):
                context = self.get_context_data()
                context['password_error'] = 'Спочатку підтвердіть зміну пароля через код'
                return self.render_to_response(context)
            
            form = EditPasswordForm(user = user, data = request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                # Очищаем флаг верификации после успешной смены пароля
                request.session.pop('password_verified', None)
                request.session.modified = True
                return redirect('settings')
            else:
                print(form.errors)
                context = self.get_context_data()
                context['edit_password_form'] = form
                return self.render_to_response(context)

        elif 'edit_user_data' in request.POST:
            # редагування профілю
            form = EditUserDataForm(request.POST, instance=user)

            if form.is_valid():
                user = form.save(commit=False)
                birth_date = form.cleaned_data.get('birth_date')
                profile, created = Profile.objects.get_or_create(user=user)
                profile.date_of_birth = birth_date
                profile.save()
                user.save()
                return redirect('settings')
            else:
                context = self.get_context_data()
                context['edit_user_data_form'] = form
                return self.render_to_response(context)
            
        elif 'edit_profile_card' in request.POST:
            username_form = EditUsernameForm(request.POST, instance=user)
            profile = Profile.objects.get(user=user)

            if username_form.is_valid():
                username_form.save()

            uploaded_file = request.FILES.get('new_avatar')
            action = request.POST.get('action_type')

            if uploaded_file and action:
                if action == 'add_avatar':
                    Avatar.objects.create(
                        image=uploaded_file,
                        profile=profile,
                        active=False,
                        shown=True
                    )
                elif action == 'select_avatar':
                    # всі неактивними
                    Avatar.objects.filter(profile=profile).update(active=False)
                    # створюємо нову активну
                    Avatar.objects.create(
                        image=uploaded_file,
                        profile=profile,
                        active=True,
                        shown=True
                    )

            return redirect('settings')

        return self.render_to_response(self.get_context_data())

def render_album_page(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        if 'create_album' in request.POST:
            create_album_form = CreateAlbumForm(request.POST, request.FILES)
            if create_album_form.is_valid():
                new_album = create_album_form.save(commit=False)
                new_album.author = profile  # Устанавливаем автора альбома
                new_album.topic = create_album_form.cleaned_data['topic']
                new_album.save()
                create_album_form.save_m2m()
                return redirect('albums')
            
        elif 'edit_album' in request.POST:
            album_id = request.POST.get('album_id')
            album = get_object_or_404(Album, id=album_id, author=profile)  # Проверяем что альбом принадлежит пользователю
            edit_album_form = EditAlbumForm(request.POST, request.FILES, instance=album)

            if edit_album_form.is_valid():
                edit_album_form.save()
                return redirect('albums')

    # Показываем только альбомы текущего пользователя
    albums = Album.objects.filter(author=profile)
    album_availability = albums.exists()

    albums_with_images = []
    for album in albums:
        albums_with_images.append({
            'album': album,
            'images': album.images.all(),
            'image_count': album.images.count()
        })

    return render(
        request,
        'my_settings/albums.html',
        context={
            'user': user,
            'edit_album_form': EditAlbumForm(),
            'create_album_form': CreateAlbumForm(),
            'album_availability': album_availability,
            'albums_with_images': albums_with_images
        }
    )

@csrf_exempt
@require_POST
def ajax_delete_album(request):
    try:
        data = json.loads(request.body)
        album_id = data.get('album_id')

        if not album_id:
            return JsonResponse({'success': False, 'error': 'album_id is required'})

        profile = Profile.objects.get(user=request.user)
        album = Album.objects.get(id=album_id, author=profile)  # Проверяем что альбом принадлежит пользователю
        album.delete()

        return JsonResponse({'success': True})

    except Album.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Альбом не знайдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def ajax_upload_photo(request):
    if request.method == 'POST':
        album_id = request.POST.get('album_id')
        uploaded_file = request.FILES.get('file')

        if not album_id or not uploaded_file:
            return JsonResponse({'success': False, 'error': 'Missing data'})

        try:
            profile = Profile.objects.get(user=request.user)
            album = Album.objects.get(id=album_id, author=profile)  # Проверяем что альбом принадлежит пользователю
            new_image = Image.objects.create(
                filename=uploaded_file.name,
                file=uploaded_file
            )
            album.images.add(new_image)

            return JsonResponse({
                'success': True,
                'image_url': new_image.file.url,
                'filename': new_image.filename,
                'image_id': new_image.id
            })

        except Album.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@require_POST
def ajax_upload_user_photo(request):
    uploaded_file = request.FILES.get('file')
    user = request.user

    if not uploaded_file:
        return JsonResponse({'success': False, 'error': 'No file'})

    try:
        profile = Profile.objects.get(user=user)
        new_avatar = Avatar.objects.create(
            image = uploaded_file,
            profile = profile,
            active = False,
            shown = True
        )
        return JsonResponse({
            'success': True,
            'image_url': new_avatar.image.url,
            'avatar_id': new_avatar.id
        })

    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'})

@csrf_exempt
@require_POST
def send_password_verification_code(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    user = request.user
    email = user.email
    code = str(random.randint(100000, 999999))

    # Сохраняем код в сессии
    session_key = f"password_verification_code_{email}"
    request.session[session_key] = code
    request.session['show_password_modal'] = True
    request.session.modified = True

    try:
        # Отправляем email с кодом
        send_mail(
            subject="Код підтвердження зміни пароля",
            message=f"Ваш код підтвердження для зміни пароля: {code}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Новые AJAX views для дополнительного функционала

@csrf_exempt
@require_POST
def ajax_toggle_album_visibility(request):
    """Переключение видимости альбома"""
    try:
        data = json.loads(request.body)
        album_id = data.get('album_id')

        if not album_id:
            return JsonResponse({'success': False, 'error': 'album_id is required'})

        profile = Profile.objects.get(user=request.user)
        album = Album.objects.get(id=album_id, author=profile)
        
        # Переключаем видимость
        album.shown = not album.shown
        album.save()

        return JsonResponse({
            'success': True,
            'shown': album.shown
        })

    except Album.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Альбом не знайдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def ajax_delete_album_photo(request):
    """Удаление фото из альбома"""
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        album_id = data.get('album_id')

        if not image_id or not album_id:
            return JsonResponse({'success': False, 'error': 'image_id and album_id are required'})

        profile = Profile.objects.get(user=request.user)
        album = Album.objects.get(id=album_id, author=profile)
        image = Image.objects.get(id=image_id)
        
        # Удаляем фото из альбома
        album.images.remove(image)
        
        # Проверяем, используется ли фото в других альбомах или постах
        other_albums = Album.objects.filter(images=image).exclude(id=album_id)
        posts_with_image = image.posts_authored.all()
        
        # Если фото не используется нигде еще, удаляем его полностью
        if not other_albums.exists() and not posts_with_image.exists():
            image.delete()

        return JsonResponse({'success': True})

    except (Album.DoesNotExist, Image.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Альбом або фото не знайдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def ajax_delete_user_photo(request):
    """Удаление пользовательского фото (аватара)"""
    try:
        data = json.loads(request.body)
        avatar_id = data.get('avatar_id')

        if not avatar_id:
            return JsonResponse({'success': False, 'error': 'avatar_id is required'})

        profile = Profile.objects.get(user=request.user)
        avatar = Avatar.objects.get(id=avatar_id, profile=profile)
        
        avatar.delete()

        return JsonResponse({'success': True})

    except Avatar.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Аватар не знайдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
