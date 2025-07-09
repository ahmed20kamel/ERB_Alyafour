from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import customer_dashboard_stats
from .views import (
    CustomerViewSet,
    CountryViewSet,
    CityViewSet,
    GenderViewSet,
    NationalityViewSet,
    BillingViewSet,
    CurrencyViewSet,
    ClassificationViewSet,
    CommunicationMethodViewSet,
)

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"countries", CountryViewSet)
router.register(r"cities", CityViewSet)
router.register(r"genders", GenderViewSet)
router.register(r"nationalities", NationalityViewSet)
router.register(r"billings", BillingViewSet)
router.register(r"currencies", CurrencyViewSet)
router.register(r"classifications", ClassificationViewSet)
router.register(r"communication-methods", CommunicationMethodViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("customers-dashboard-stats/", customer_dashboard_stats),
]
