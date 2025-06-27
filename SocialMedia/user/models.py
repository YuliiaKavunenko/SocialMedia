from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    signature = models.ImageField(upload_to = 'images/signatures', blank=True, null=True)

    def __str__(self):
        
        return self.user.username

class Avatar(models.Model):
    image = models.ImageField(upload_to='images/avatars')
    profile = models.ForeignKey(Profile, on_delete = models.CASCADE)
    active = models.BooleanField(default=True) # Чи активна ця аватарка (чи використовується вона у профілі)
    shown = models.BooleanField(default=True) # Чи показана ця аватарка в альбомі минулих аватарок

    def __str__(self):
        return f'Аватар для профілю {self.profile}'


class Friendship(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friendship_sent_request') # Той, хто надіслав запит на дружбу
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friendship_accepted_request') # Той, хто має прийняти запит на дружбу
    accepted = models.BooleanField(default=False) # Чи прийнято запит на дружбу

    def __str__(self):
        return f'Дружба між {self.profile1} та {self.profile2}'



class VerificationCode(models.Model):
    username = models.CharField(max_length=150)
    code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)