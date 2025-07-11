# Generated by Django 5.1.4 on 2025-06-16 06:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=150)),
                ('file', models.ImageField(upload_to='images/posts')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(max_length=4096)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.profile')),
                ('images', models.ManyToManyField(blank=True, related_name='posts_authored', to='main_page.image')),
                ('likes', models.ManyToManyField(blank=True, related_name='posts_liked', to='user.profile')),
                ('views', models.ManyToManyField(blank=True, related_name='posts_viewed', to='user.profile')),
                ('tags', models.ManyToManyField(blank=True, to='main_page.tag')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_page.post')),
            ],
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('preview_image', models.ImageField(blank=True, null=True, upload_to='images/album_previews')),
                ('shown', models.BooleanField(default=True)),
                ('images', models.ManyToManyField(blank=True, to='main_page.image')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_page.tag')),
            ],
        ),
    ]
