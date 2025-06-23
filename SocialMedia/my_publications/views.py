from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from main_page.models import Post, Tag, Image, Link
from user.models import Avatar
from main_page.forms import CreatePublicationsForm
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
            publication.author = request.user.profile
            publication.save()

            # Обработка тегов для редактирования
            selected_tags = request.POST.get('selected_tags', '')
            tag_ids = [int(tid) for tid in selected_tags.split(',') if tid.isdigit()]
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
                # НЕ очищаем старые изображения, только добавляем новые
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
            publication.author = user.profile
            publication.save()

            # Теги
            selected_tags = request.POST.get('selected_tags', '')
            tag_ids = [int(tid) for tid in selected_tags.split(',') if tid.isdigit()]
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
            return JsonResponse({
                'status' : 'success',
                'tag' : tag_object.name,
                'id' : tag_object.id,
                'created' : created
            })
    else:
        return JsonResponse({"status": "error", "message": "Порожній тег"})
