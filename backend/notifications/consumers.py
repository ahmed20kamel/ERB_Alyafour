# notifications/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.group_name = None

        if user.is_anonymous:
            print("🔴 CONSUMER DEBUG: anonymous user tried to connect, closing.")
            await self.close()
        else:
            self.group_name = f"notifications_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"🟢 CONSUMER DEBUG: accepted websocket for user={user.username} id={user.id}")

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"🔴 CONSUMER DEBUG: disconnected user={self.scope['user'].username}")
        else:
            print("⚠️ CONSUMER DEBUG: disconnect called without group_name (maybe anonymous)")

    async def receive_json(self, content):
        print(f"CONSUMER DEBUG: received from client: {content}")
        await self.send_json({
            "status": "received",
            "message": "no action performed"
        })

    async def send_notification(self, event):
        notification = {
            "id": event.get("id"),
            "title": event.get("title", "No Title"),
            "message": event.get("message", "No Message"),
            "is_read": event.get("is_read", False),
            "created_at": event.get("created_at"),
        }
        await self.send_json(notification)
        print(f"🟢 CONSUMER DEBUG: sent to user {self.scope['user'].username}")
