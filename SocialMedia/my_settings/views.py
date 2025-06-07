from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main_page.models import UserPublications

class SettingsPageViews(LoginRequiredMixin, TemplateView):
    template_name = 'my_settings/my_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['user_publications_count'] = UserPublications.objects.filter(user=user).count()
        return context
