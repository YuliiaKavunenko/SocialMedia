from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.render_user, name='user'),
    path('login/', views.render_login, name='login'),
    path('registration/', views.render_registration, name='registration'),
    path('logout/', views.user_logout, name='logout'),
]
