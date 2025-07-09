# notifications/models.py
from django.db import models
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # بعد ما يتسجل في db ابعته للـ group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{self.user.id}",
            {
                "type": "send_notification",
                "id": self.id,
                "title": self.title,
                "message": self.body,
                "is_read": self.is_read,
                "created_at": self.created_at.isoformat(),
            }
        )
