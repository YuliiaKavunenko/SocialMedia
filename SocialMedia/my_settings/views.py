from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import EditUserDataForm, EditUsernameForm, EditAlbumForm, CreateAlbumForm, EditPasswordForm
from main_page.models import Album, Image
from user.models import Avatar
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.csrf import csrf_exempt
from user.models import Profile
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
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


        return context
    def post(self, request, *args, **kwargs):
        user = request.user

        if 'edit_password' in request.POST:
            form = EditPasswordForm(user = user, data = request.POST)
            if form.is_valid():
                # print("Form is valid")
                # print(user.password)
                form.save()
                update_session_auth_hash(request, form.user)
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

    if request.method == 'POST':
        if 'create_album' in request.POST:
            create_album_form = CreateAlbumForm(request.POST, request.FILES)
            if create_album_form.is_valid():
                new_album = create_album_form.save(commit=False)
                new_album.topic = create_album_form.cleaned_data['topic']
                new_album.save()
                create_album_form.save_m2m()
                return redirect('albums')
            
        elif 'edit_album' in request.POST:
            # print(request.POST)
            album_id = request.POST.get('album_id')
            album = get_object_or_404(Album, id = album_id)
            edit_album_form = EditAlbumForm(request.POST, request.FILES, instance = album)

            if edit_album_form.is_valid():
                edit_album_form.save()
                return redirect('albums')


    albums = Album.objects.all()
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

        album = Album.objects.get(id=album_id)
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
            album = Album.objects.get(id=album_id)
            new_image = Image.objects.create(
                filename=uploaded_file.name,
                file=uploaded_file
            )
            album.images.add(new_image)

            return JsonResponse({
                'success': True,
                'image_url': new_image.file.url,
                'filename': new_image.filename
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
            'image_url': new_avatar.image.url
        })

    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'})
