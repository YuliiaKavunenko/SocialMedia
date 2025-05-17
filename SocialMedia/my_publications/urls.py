from django.urls import path
from . import views

urlpatterns = [
    path('my_publications/', views.render_my_publications_page, name = 'my_publications'),
]

