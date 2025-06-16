from django.urls import path
from . import views

urlpatterns = [
    path('my_publications/', views.render_my_publications_page, name = 'my_publications'),
    path('delete-publication/<int:pub_id>/', views.delete_publication, name='delete_publication'),
    path('edit_publications/<int:pub_id>', views.edit_publication, name = 'edit_publication'),
    path('add_tag/', views.add_tag, name = 'add_tag'),
]

