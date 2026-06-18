from django.urls import path
from insights.views import SmartSearchView, UserInterestsView, AdminDemandForecastView

urlpatterns = [
    path('search/', SmartSearchView.as_view(), name='smart-search'),
    path('user-interests/', UserInterestsView.as_view(), name='user-interests'),
    path('admin/demand-forecast/', AdminDemandForecastView.as_view(), name='admin-demand-forecast'),
]
