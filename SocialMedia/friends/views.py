from django.shortcuts import render
from django.views import View
# Create your views here.
class FriendsPageViews(View):
    template_name = 'friends/friends.html'
    def get(self, request):
        return render(request, self.template_name)