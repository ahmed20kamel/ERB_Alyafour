from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT Auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # App APIs
    path("api/", include("customers.urls")),
    path("api/shared/", include("shared.urls")),
    path("api/approvals/", include("approvals.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/docs/", include("erp_system.api.docs_urls")),
    path("api/", include("suppliers.urls")),
    path("api/", include("projects.urls")),
    path("api/files/", include("files.api_urls")),          # ✅ REST API for files app

    # ✅ Pre-Tender APIs (التطبيق الجديد)
    # متركبة تحت بادئة ثابتة عشان ما يحصلش تعارض مع باقي الـ apps
    path("api/pre-tender/", include("pre_tender.api_urls")),
]

# Static/media for dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
