# erp_system/asgi.py

import os
import sys
import django

# ✅ إضافة مسار backend إلى sys.path (لو داخل backend فعليًا)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(BASE_DIR, "backend")
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from notifications.routing import websocket_urlpatterns  # ✅ بدون backend

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

django_application = get_asgi_application()

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token["user_id"]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        from datetime import datetime
        from django.utils.timezone import make_aware

        query_string = scope.get("query_string", b"").decode()
        token_param = parse_qs(query_string).get("token")
        scope["user"] = AnonymousUser()

        if token_param:
            try:
                token = AccessToken(token_param[0])
                exp_timestamp = int(token["exp"])
                now_timestamp = int(make_aware(datetime.utcnow()).timestamp())

                if now_timestamp >= exp_timestamp:
                    print("❌ JWTAuthMiddleware: token expired")
                    return await self.app(scope, receive, send)

                user = await get_user(token)
                scope["user"] = user
                print(f"✅ JWTAuthMiddleware: connected user={user.username}")
            except Exception as e:
                print(f"❌ JWTAuthMiddleware token error => {e}")
        else:
            print("❌ JWTAuthMiddleware: no token found")

        return await self.app(scope, receive, send)


application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
