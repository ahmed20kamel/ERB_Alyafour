from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, SupplierGroupViewSet, ScopeOfWorkViewSet,
    SupplierContactPersonViewSet, SupplierLegalPersonViewSet
)

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"supplier-groups", SupplierGroupViewSet, basename="supplier-group")
router.register(r"scopes-of-work", ScopeOfWorkViewSet, basename="scope-of-work")
router.register(r"supplier-contact-people", SupplierContactPersonViewSet, basename="supplier-contact-person")
router.register(r"supplier-legal-person", SupplierLegalPersonViewSet, basename="supplier-legal-person")

urlpatterns = router.urls
