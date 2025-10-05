from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, VariationOrderViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"variation-orders", VariationOrderViewSet, basename="variation-orders")
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
]
