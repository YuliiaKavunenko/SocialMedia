from django.contrib import admin
from .models import Profile, Avatar, VerificationCode, Friendship
# Register your models here.
admin.site.register(Profile)
admin.site.register(Avatar)
admin.site.register(VerificationCode)
admin.site.register(Friendship)