from django.shortcuts import render

# Create your views here.
def render_my_publications_page(request):
    return render(
        request = request,
        template_name = "my_publications/my_publications.html"
    )