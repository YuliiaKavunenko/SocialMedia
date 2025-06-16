from django.shortcuts import render, redirect
from .forms import CreatePublicationsForm
from .models import Post
from django.contrib.auth.decorators import login_required
from .forms import UserProfileUpdateForm
# Create your views here.



@login_required
def render_main_page(request):
    user = request.user

    force_update = 'force_update_profile' in request.POST

    if user.username == user.email or force_update:
        if request.method == 'POST' and force_update:
            profile_form = UserProfileUpdateForm(request.POST, instance = user)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('settings')
        else:
            profile_form = UserProfileUpdateForm(instance=user)

        publication_form = CreatePublicationsForm()
        user_publications_count = Post.objects.filter(user = user.profile).count()
        return render(request, 'main_page/main_page.html', {
            "user": user,
            "form": publication_form,
            "publications": Post.objects.all(),
            "show_additional_info_modal": True,
            "profile_form": profile_form,
            "user_publications_count": user_publications_count
        })

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = user.profile
            publication.views = 0
            publication.likes = 0
            publication.save()
            return redirect('main_page')
    else:
        form = CreatePublicationsForm()

    user_publications_count = Post.objects.filter(author = user.profile).count()
    return render(request, 'main_page/main_page.html', {
        "user": user,
        "form": form,
        "publications": Post.objects.all(),
        "show_additional_info_modal": False,
        "profile_form": UserProfileUpdateForm(instance=user),
        "user_publications_count": user_publications_count
    })
