from .models import Post, Tag
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

class CreatePublicationsForm(forms.ModelForm):
    # theme = forms.CharField(required = False, help_text = 'Напишіть тему публікації')
    tags = forms.ModelMultipleChoiceField(
        queryset = Tag.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = False
    )
    # url = forms.URLField(required = False)
    images = forms.ImageField(required=False)
    class Meta:
        model = Post
        fields = ['title','tags', 'content', 'images']#['title', 'theme', 'tags', 'text', 'url', 'images']
        widgets = {
            'title': forms.TextInput(attrs = {
                'placeholder': 'Природа, книга і спокій 🌿',
                'class':'publication-form-input',
                'id': 'form-title'
            }),
            # 'theme': forms.TextInput(attrs = {
            #     'placeholder': 'Напишіть тему публікації', 
            #     'class':'publication-form-input',
            #     'id': 'form-theme'
            # }),
            'content': forms.Textarea(attrs = {
                'placeholder': 'Інколи найкращі ідеї народжуються в тиші. Природа, книга і спокій — усе, що потрібно, аби перезавантажитись.', 
                'id': 'form-text',
            }),
            # 'url': forms.URLInput(attrs = {
            #     'placeholder': 'https://www.instagram.com/world.it.academy/?locale=ua', 
            #     'class':'publication-form-input',
            #     'id': 'form-url'
            # }),
            'images': forms.ClearableFileInput(attrs = {
                'id': 'image-field',
            }),
        }
        labels = {
            'title': 'Назва публікації',
            # 'theme': 'Тема публікації',
            'tags': 'Теги публікації',
            'content': '',
            # 'url': 'Посилання',
            'images': ''
        }
    def clean(self):
        cleaned_data = super().clean()

        url = cleaned_data.get('url')

        if url and not url.startswith('https://'):
            self.add_error('url', 'Посилання має починатись з "https://"')

        return cleaned_data

class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Ім’я',
        widget=forms.TextInput(attrs = {'placeholder': 'Введіть Ваше ім’я'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Прізвище',
        widget=forms.TextInput(attrs = {'placeholder': 'Введіть Ваше прізвище'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Ім’я користувача',
        widget=forms.TextInput(attrs = {'placeholder': '@'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Це ім’я користувача вже зайняте.')
        return username
