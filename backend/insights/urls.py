from django.urls import path
from insights.views import SmartSearchView, UserInterestsView

urlpatterns = [
    path('search/', SmartSearchView.as_view(), name='smart-search'),
    path('user-interests/', UserInterestsView.as_view(), name='user-interests'),
]
