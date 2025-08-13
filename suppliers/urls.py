from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, ScopeOfWorkViewSet, SupplierGroupViewSet

router = DefaultRouter()
router.register(r'', SupplierViewSet, basename='supplier')
router.register(r'scope-of-work', ScopeOfWorkViewSet, basename='scope-of-work')
router.register(r'supplier-groups', SupplierGroupViewSet, basename='supplier-group')

urlpatterns = [
    path('', include(router.urls)),
]
