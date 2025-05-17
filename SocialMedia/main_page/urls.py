from django.urls import path
from . import views

urlpatterns = [
    path('', views.render_main_page, name = 'main_page'),
    path('delete-publication/<int:pub_id>/', views.delete_publication, name='delete_publication'),

]

