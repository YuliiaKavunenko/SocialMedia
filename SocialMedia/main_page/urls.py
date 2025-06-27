from django.urls import path
from . import views

urlpatterns = [
    path('', views.render_main_page, name = 'main_page'),
    path('add-tag/', views.add_tag, name='add_tag'),
]
