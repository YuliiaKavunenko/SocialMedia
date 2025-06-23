from django import forms
from django.contrib.auth.models import User

# Форма для реєстрації користувача
class RegistrationForm(forms.ModelForm):
    # Додаткове поле для підтвердження паролю
    confirm_password = forms.CharField(
        widget = forms.PasswordInput(attrs = {'placeholder': 'Повтори пароль'}),
        label = "Підтвердіть пароль"
    )

    class Meta:
        model = User  # Вказуємо модель, на основі якої будується форма
        fields = ['email', 'password']  # Основні поля форми
        labels = {
            'email': 'Електронна пошта',
            'password': 'Пароль'
        }
        widgets = {
            'password': forms.PasswordInput(attrs = {'placeholder': 'Введи пароль'}),
            'email': forms.EmailInput(attrs = {'placeholder': 'you@example.com'}),
        }

    # Метод перевірки правильності заповнення форми
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        user = User.objects.filter(username=email).first()
        if user and user.is_active:
            raise forms.ValidationError("Користувач з такою електронною поштою вже існує.")

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Паролі не співпадають")

        return cleaned_data
    def save(self, commit=True):
        user = super().save(commit = False)
        user.username = self.cleaned_data['email']
        #хешуємо пароль
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# Форма для авторизації користувача
class LogInForm(forms.Form):
    email = forms.CharField(
        label = "Електронна пошта",
        widget = forms.TextInput(attrs = {'placeholder': "you@example.com"})
    )

    password = forms.CharField(
        label = "Пароль",
        widget = forms.PasswordInput(attrs = {'placeholder': 'Введи пароль'})
    )