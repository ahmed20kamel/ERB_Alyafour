# backend/erp_system/asgi.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs

from notifications.routing import websocket_urlpatterns

django_application = get_asgi_application()
User = get_user_model()


class JWTAuthMiddleware:
    """
    Custom JWT middleware for channels
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token")

        if token:
            try:
                access_token = AccessToken(token[0])
                user_id = access_token["user_id"]
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                scope["user"] = user
                print(f"✅ JWTAuthMiddleware: connected user={user.username}")
            except Exception as e:
                print(f"❌ JWTAuthMiddleware token error => {e}")
                scope["user"] = AnonymousUser()
        else:
            print("❌ JWTAuthMiddleware: no token found")
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)


application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
