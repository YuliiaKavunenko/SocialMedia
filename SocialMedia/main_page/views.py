from django.shortcuts import render, redirect
from .forms import CreatePublicationsForm
from .models import Post
from django.contrib.auth.decorators import login_required
from .forms import UserProfileUpdateForm
from .models import Profile, Image, Link
from user.models import Avatar
# Create your views here.



@login_required
def render_main_page(request):
    user = request.user

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = user.profile
            publication.save()

            # Теги
            tags = form.cleaned_data.get('tags')
            if tags:
                publication.tags.set(tags)
            else:
                publication.tags.clear()

            # Зображення — обробка множинних файлів
            images_files = request.FILES.getlist('images')
            for img in images_files:
                image_obj = Image.objects.create(filename=img.name, file=img)
                publication.images.add(image_obj)

            urls = request.POST.getlist('urls')
            for url in urls:
                url = url.strip()
                if url:
                    Link.objects.create(post = publication, url=url)

            return redirect('main_page')

    else:
        form = CreatePublicationsForm()

    user_publications_count = Post.objects.filter(author=user.profile).count()
    publications = Post.objects.all().prefetch_related('tags', 'images', 'link_set').order_by('-id')

    return render(request, 'main_page/main_page.html', {
        "user": user,
        "form": form,
        "publications": publications,
        "user_publications_count": user_publications_count,
        "show_additional_info_modal": False,
    })

