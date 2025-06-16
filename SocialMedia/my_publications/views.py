from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from main_page.models import Post, Tag
from main_page.forms import CreatePublicationsForm #, NewTagForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def edit_publication(request, pub_id):
    publication = get_object_or_404(Post, id=pub_id)

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = request.user
            publication.views = 0
            publication.likes = 0
            publication.save()

            form.save_m2m()

            return redirect('main_page')
    else:
        form = CreatePublicationsForm(instance=publication)

    return render(
        request,
        "main_page/main.page.html",
        {
            "user": request.user,
            "form": form,
            "publication": publication,
        }
    )

@login_required
def delete_publication(request, pub_id):
    publication = get_object_or_404(Post, id = pub_id)

    if request.method == "POST":
        publication.delete()
        return redirect('my_publications')
    
def render_my_publications_page(request):
    user = request.user
    form = CreatePublicationsForm()

    if request.method == 'POST':
        print("POST request received")
        form = CreatePublicationsForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            publication = form.save(commit=False)
            publication.author = user.profile
            publication.views = 0
            publication.likes = 0

            # Посилання
            urls = []
            if form.cleaned_data['url']:
                urls.append(form.cleaned_data['url'])

            extra_urls = request.POST.getlist('extra_url')
            for url in extra_urls:
                if url.strip():
                    urls.append(url)

            publication.url = '\n'.join(urls)

            selected_tags = request.POST.get('selected_tags', '')
            tag_ids = [
                int(tid)
                for tid in selected_tags.split(',')
                if tid.isdigit()
            ]
            

            publication.save()
            if tag_ids:
                publication.tags.set(tag_ids)
            form.save_m2m()

            return redirect('my_publications')

    # user_publications_count = Post.objects.filter(user = user.profile).count()

    return render(request, "my_publications/my_publications.html", {
        "user": user,
        "form": form,
        "publications": Post.objects.all(),
        # "user_publications_count": user_publications_count
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
            return JsonResponse({"status": "error", "message": "Порожній тег"})