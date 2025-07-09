from django.urls import path
from .views import NotificationListAPIView, NotificationMarkAsReadAPIView

urlpatterns = [
    path(
        "notifications/",
        NotificationListAPIView.as_view(),
        name="notifications-list",
    ),
    path(
        "notifications/<int:id>/read/",
        NotificationMarkAsReadAPIView.as_view(),
        name="notifications-read",
    ),
]
