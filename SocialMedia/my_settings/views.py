from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class SettingsPageViews(TemplateView):
    template_name = 'my_settings/my_settings.html'

