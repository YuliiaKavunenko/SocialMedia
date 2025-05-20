from django.shortcuts import render, redirect
from .forms import CreatePublicationsForm
from .models import UserPublications
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
# Create your views here.

@login_required
def edit_publication(request, pub_id):
    publication = get_object_or_404(UserPublications, id = pub_id)
    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES, instance = publication)
        if form.is_valid():
            publication = form.save(commit = False)
            publication.user = request.user
            publication.views = 0
            publication.likes = 0
            publication.save()
            return redirect('main_page')
    else:
        form = CreatePublicationsForm(instance = publication)
    
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
    publication = get_object_or_404(UserPublications, id = pub_id)

    if request.method == "POST":
        publication.delete()
        return redirect('main_page')

def render_main_page(request):

    if not request.user.is_authenticated:
        return redirect('registration')

    if request.method == 'POST':
        form = CreatePublicationsForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.user = request.user
            publication.views = 0
            publication.likes = 0
            publication.save()
            return redirect('main_page')
    else:
        form = CreatePublicationsForm()

    publications = UserPublications.objects.all()

    return render(
        request,
        "main_page/main_page.html",
        {
            "user": request.user,
            "form": form,
            "publications": publications,
        }
    )