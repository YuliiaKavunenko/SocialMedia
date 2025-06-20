from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from main_page.models import Album, Tag, Profile

class EditUserDataForm(forms.ModelForm):
    birth_date = forms.DateField(
        required = False,
        widget=forms.DateInput(attrs = {
            'type': 'date',
            'class': 'edit-profile-input',
            'placeholder': 'дд.мм.рррр',
            'id': 'birth-date-input',
            'readonly': 'readonly',
            'disabled': 'disabled',
        }),
        label = 'Дата народження'
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs = {
                'class': 'edit-profile-input',
                'placeholder': 'Lina',
                'id': 'name-input',
                'readonly': 'readonly',
                'disabled': 'disabled',
            }),
            'last_name': forms.TextInput(attrs = {
                'class': 'edit-profile-input',
                'placeholder': 'Li',
                'id': 'surname-input',
                'readonly': 'readonly',
                'disabled': 'disabled',
            }),
            'email': forms.EmailInput(attrs = {
                'class': 'edit-profile-input',
                'placeholder': 'you@example.com',
                'id': 'email-input',
                'readonly': 'readonly',
                'disabled': 'disabled',
            }),
        }
        labels = {
            'first_name': 'Ім’я',
            'last_name': 'Прізвище',
            'email': 'Електронна адреса',
            
        }

class EditPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(EditPasswordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'edit-profile-input',
                'placeholder': '*********',
                'disabled': 'disabled',
            })

class EditUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'edit-profile-input',
                'placeholder': '@',
                'id': 'username-input',
            }),
        }
        labels = {
            'username': 'Ім’я користувача',
        }

class CreateAlbumForm(forms.ModelForm):
    year = forms.ChoiceField(
        choices = [(year, str(year)) for year in range(1980, 2026)],
        initial = 2025,
        widget = forms.Select(attrs = {
            'class': 'edit-profile-input',
            'id': 'year-input',
        }),
        label = 'Рік альбому'
    )
    topic = forms.ModelChoiceField(
        queryset = Tag.objects.all(),
        widget=forms.Select(attrs={
            'class': 'edit-profile-input',
            'id': 'topic-input',
        }),
        label = 'Тема альбому',
        initial = 0,
    )

    class Meta:
        model = Album
        fields = ['name', 'topic', 'year']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Настрій',
                'class': 'edit-profile-input',
            }),
        }
        labels = {
            'name': 'Назва альбому',
        }

class EditAlbumForm(forms.ModelForm):

    year = forms.ChoiceField(
        choices = [(year, str(year)) for year in range(1980, 2026)],
        initial = 2025,
        widget = forms.Select(attrs = {
            'class': 'edit-profile-input',
            'id': 'edit-year-input',
        }),
        label = 'Рік альбому'
    )
    topic = forms.ModelChoiceField(
        queryset = Tag.objects.all(),
        widget=forms.Select(attrs={
            'class': 'edit-profile-input',
            'id': 'edit-topic-input',
        }),
        label = 'Тема альбому',
        initial = 0,
    )

    class Meta:
        
        model = Album
        fields = ['name', 'topic', 'year']
        widgets = {
            'name': forms.TextInput(attrs = {
                'placeholder': 'Настрій',
                'class': 'edit-profile-input',
                'id': 'edit-name-input',
            }),
        }
        labels = {
            'name': 'Назва альбому',
        }