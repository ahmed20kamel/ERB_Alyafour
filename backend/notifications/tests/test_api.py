import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

@pytest.mark.django_db
def test_create_notification():
    user = User.objects.create_user(username="testuser", password="testpass")
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "user": user.id,
        "title": "Test notification",
        "body": "Test body"
    }
    response = client.post("/api/core/notifications/create/", data)
    assert response.status_code == 201
    notif = Notification.objects.first()
    assert notif.title == "Test notification"
