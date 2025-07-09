# core/consumers.py
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        logger.debug(f"connect: user={user}")

        if user.is_anonymous:
            logger.warning("anonymous user tried to connect, closing websocket")
            await self.close()
        else:
            try:
                await self.channel_layer.group_add(
                    f"notifications_{user.id}",
                    self.channel_name
                )
                await self.accept()
                logger.debug(f"accepted websocket for user {user.id}")
            except Exception as e:
                logger.error(f"error on connect: {e}")
                await self.close()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        logger.debug(f"disconnect: user={user}")
        await self.channel_layer.group_discard(
            f"notifications_{user.id}",
            self.channel_name
        )

    async def receive_json(self, content):
        logger.debug(f"received json: {content}")
        # لو حبيت تتعامل مع رسائل من الكلاينت هنا في المستقبل

    async def send_notification(self, event):
        logger.debug(f"sending notification: {event}")
        await self.send_json({
            "title": event["title"],
            "message": event["message"],
        })
