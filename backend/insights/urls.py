from django.urls import path
from insights.views import SmartSearchChatView

urlpatterns = [
    path('chat/', SmartSearchChatView.as_view(), name='smart-search-chat'),
]
