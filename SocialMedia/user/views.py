import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LogInForm
from django.contrib.auth.models import User
from django.core.mail import send_mail


# Відповідає за реєстрацію користувача
def render_registration(request):
    if request.method == "POST":
        if request.POST.get("action") == "confirm_code":
            # Користувач ввів код підтвердження
            email = request.POST.get("email")
            code_parts = [request.POST.get(f"code{i}") for i in range(1, 7)]
            code = ''.join(code_parts)

            # Получаем код из сессии
            session_key = f"verification_code_{email}"
            stored_code = request.session.get(session_key)

            if stored_code and stored_code == code:
                try:
                    user = User.objects.get(email=email)
                    user.is_active = True
                    user.save()
                    
                    # Удаляем код из сессии после успешного подтверждения
                    del request.session[session_key]
                    request.session.modified = True
                    
                    return redirect("login")
                except User.DoesNotExist:
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

                        # Сохраняем код в сессии
                        session_key = f"verification_code_{email}"
                        request.session[session_key] = code
                        request.session.modified = True

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

                    # Сохраняем код в сессии
                    session_key = f"verification_code_{user.email}"
                    request.session[session_key] = code
                    request.session.modified = True

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
    error = None
    if request.method == "POST":
        form = LogInForm(request.POST)  # Отримуємо дані з форми
        if form.is_valid():
            email = form.cleaned_data['email']  # Отримуємо логін
            password = form.cleaned_data['password']  # Отримуємо пароль

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            user = authenticate(request=request, username=user.username, password=password)

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
            "form": form,
            "error": error,
        }
    )

# Відображає сторінку кабінету користувача
def render_user(request):
    return render(
        request = request,
        template_name = "user/user.html",
        context = {
            "user": request.user,
        }
    )

def user_logout(request):
    logout(request)  # Вихід користувача
    return redirect('login')
