from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserPublications(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 100)
    theme = models.CharField(max_length = 255)
    tags = models.ManyToManyField('StandartTags', blank = True)
    text = models.TextField()
    url = models.URLField()
    images = models.ImageField(upload_to = 'images/')
    views = models.IntegerField()
    likes = models.IntegerField()

    def __str__(self):
        return self.title

class StandartTags(models.Model):
    tag = models.CharField(max_length = 100)

    def __str__(self):
        return self.tag