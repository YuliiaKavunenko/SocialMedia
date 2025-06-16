import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LogInForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import VerificationCode


# Відповідає за реєстрацію користувача
def render_registration(request):
    if request.method == "POST":
        if request.POST.get("action") == "confirm_code":
            # Користувач ввів код підтвердження
            email = request.POST.get("email")
            code_parts = [request.POST.get(f"code{i}") for i in range(1, 7)]
            code = ''.join(code_parts)

            try:
                user = User.objects.get(email=email)
                confirmation = VerificationCode.objects.get(username = user.username)

                if confirmation.code == code:
                    user.is_active = True
                    user.save()

                    confirmation.is_confirmed = True
                    confirmation.save()
                    return redirect("login")
                else:
                    form = RegistrationForm()
                    return render(
                        request,
                        "user/registration.html",
                        {
                            "form": form,
                            "show_modal": True,
                            "code_error": "Неправильний код підтвердження.",
                            "email": email,
                        }
                    )
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                form = RegistrationForm()
                return render(
                    request,
                    "user/registration.html",
                    {
                        "form": form,
                        "code_error": "Щось пішло не так. Спробуйте знову.",
                        "show_modal": False,
                    }
                )

        else:
            # Користувач надсилає форму реєстрації
            form = RegistrationForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data.get("email")
                existing_user = User.objects.filter(email=email).first()

                if existing_user:
                    if existing_user.is_active:
                        # Користувач вже активований
                        form.add_error("email", "Користувач з такою електронною поштою вже існує.")
                        return render(request, "user/registration.html", {
                            "form": form,
                            "show_modal": False
                        })
                    else:
                        # Користувач існує, але ще не підтвердив код
                        code = str(random.randint(100000, 999999))

                        confirmation, _ = VerificationCode.objects.get_or_create(username = existing_user)
                        confirmation.code = code
                        confirmation.is_confirmed = False
                        confirmation.save()

                        send_mail(
                            subject="Код підтвердження",
                            message=f"Ваш код підтвердження: {code}",
                            from_email=None,
                            recipient_list=[email],
                            fail_silently=False,
                        )

                        return render(
                            request,
                            "user/registration.html",
                            {
                                "form": form,
                                "show_modal": True,
                                "email": email,
                            }
                        )
                else:
                    # Новий користувач
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    code = str(random.randint(100000, 999999))

                    VerificationCode.objects.create(username = user.username, code = code)

                    send_mail(
                        subject="Код підтвердження",
                        message=f"Ваш код підтвердження: {code}",
                        from_email=None,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )

                    return render(
                        request,
                        "user/registration.html",
                        {
                            "form": form,
                            "show_modal": True,
                            "email": user.email,
                        }
                    )

    else:
        form = RegistrationForm()

    return render(request, "user/registration.html", {
        "form": form,
        "show_modal": False
    })



# Відповідає за вхід користувача
def render_login(request):
    error = None  # Змінна для збереження повідомлення про помилку
    if request.method == "POST":
        form = LogInForm(request.POST)  # Отримуємо дані з форми
        if form.is_valid():
            email = form.cleaned_data['email']  # Отримуємо логін
            password = form.cleaned_data['password']  # Отримуємо пароль

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            user = authenticate(request=request, username=user.username, password=password)  # Перевіряємо користувача

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('user')
                else:
                    error = "Підтвердіть вашу електронну пошту перед входом."
            else:
                error = "Неправильний email або пароль"
    else:
        form = LogInForm()

    return render(
        request = request,
        template_name = "user/login.html",
        context = {
            "form": form,  # Передаємо форму
            "error": error,  # Передаємо повідомлення про помилку (якщо є)
        }
    )

# Відображає сторінку кабінету користувача
def render_user(request):
    return render(
        request = request,
        template_name = "user/user.html",
        context = {
            "user": request.user,  # Передаємо поточного користувача у шаблон
        }
    )

# Відповідає за вихід користувача з системи
def user_logout(request):
    logout(request)  # Вихід користувача
    return redirect('login')  # Перенаправлення на сторінку входу
