from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import EditUserDataForm, EditPasswordForm, EditUsernameForm
from django.shortcuts import redirect


class SettingsPageViews(LoginRequiredMixin, TemplateView):
    template_name = 'my_settings/my_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['edit_user_data_form'] = EditUserDataForm(instance = user)
        context['edit_password_form'] = EditPasswordForm(user = self.request.user)
        context['edit_username_form'] = EditUsernameForm(instance = user)
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        form = EditUserDataForm(request.POST, instance = user)
        if form.is_valid():
            form.save()
            return redirect('settings')
        else:
            context = self.get_context_data()
            context['edit_user_data_form'] = form
            return self.render_to_response(context)

def render_album_page(request):
    user = request.user

    return render(
        request, 
        'my_settings/albums.html',
        context={
            'user': user,
        }
    )