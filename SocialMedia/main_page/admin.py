from django.contrib import admin
from .models import Post, Tag, Album, Link, Image
# Register your models here.
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Album)
admin.site.register(Link)
admin.site.register(Image)