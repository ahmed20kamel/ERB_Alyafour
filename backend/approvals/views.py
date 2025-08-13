from rest_framework.routers import DefaultRouter
from approvals.views import DeleteClientRequestViewSet

router = DefaultRouter()
router.register(r'delete-requests', DeleteClientRequestViewSet, basename='delete-request')
urlpatterns = router.urls
