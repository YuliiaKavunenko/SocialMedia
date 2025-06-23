from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.SettingsPageViews.as_view(), name = 'settings' ),
    path('settings/albums/', views.render_album_page, name = 'albums'),
    path('ajax/upload-photo/', views.ajax_upload_photo, name = 'ajax_upload_photo'),
    path('ajax/delete-album/', views.ajax_delete_album, name = 'ajax_delete_album'),
    path('ajax/upload-user-photo/', views.ajax_upload_user_photo, name = 'ajax_upload_user_photo'),

]