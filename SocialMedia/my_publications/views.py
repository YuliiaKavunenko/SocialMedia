from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from main_page.models import Post, Tag, Image, Link
from user.models import Avatar
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
    

@login_required
def render_my_publications_page(request):
    user = request.user
    form = CreatePublicationsForm()

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES)

        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = user.profile  # точно профіль
            publication.save()

            # Теги
            selected_tags = request.POST.get('selected_tags', '')
            tag_ids = [int(tid) for tid in selected_tags.split(',') if tid.isdigit()]
            if tag_ids:
                publication.tags.set(tag_ids)
            else:
                publication.tags.clear()  # щоб не лишились старі теги

            # Зображення
            uploaded_file = request.FILES.get('images')
            if uploaded_file:
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

            # form.save_m2m()
            return redirect('my_publications')

    # Відображення сторінки
    publications = Post.objects.all().prefetch_related('tags', 'images', 'link_set')

    return render(request, "my_publications/my_publications.html", {
        "user": user,
        "form": form,
        "publications": publications,
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