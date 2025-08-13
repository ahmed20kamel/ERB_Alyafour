from django.urls import path
from .views import ProfileView, NotificationListView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('notifications/', NotificationListView.as_view(), name='user-notifications'),
]
