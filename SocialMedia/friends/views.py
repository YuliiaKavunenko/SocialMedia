from django.shortcuts import render
from django.views import View
# Create your views here.
class FriendsPageViews(View):
    template_name = 'friends/friends.html'
    def get(self, request):
        return render(request, self.template_name)
class AllFriendsPageViews(View):
    template_name = 'friends/allfriends.html'
    def get(self, request):
        return render(request, self.template_name)
class RecommendationsPageViews(View):
    template_name = 'friends/recommendations.html'
    def get(self, request):
        return render(request, self.template_name)
class RequestsPageViews(View):
    template_name = 'friends/requests.html'
    def get(self, request):
        return render(request, self.template_name)