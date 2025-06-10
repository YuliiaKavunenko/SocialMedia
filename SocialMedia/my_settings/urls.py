from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.SettingsPageViews.as_view(), name= 'settings' ),
    path('settings/albums/', views.render_album_page, name = 'albums'),
]