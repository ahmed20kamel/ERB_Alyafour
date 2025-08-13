from django.urls import path
from rest_framework.routers import DefaultRouter
from shared.views import (
    CountryViewSet, CityViewSet, AreaViewSet,
    NationalityViewSet, GenderViewSet, ClassificationViewSet,
    CurrencyViewSet, CommunicationMethodViewSet, BillingViewSet,LanguageViewSet, BankViewSet
)

router = DefaultRouter()

router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("areas", AreaViewSet)
router.register("nationalities", NationalityViewSet)
router.register("genders", GenderViewSet)
router.register("classifications", ClassificationViewSet)
router.register("currencies", CurrencyViewSet)
router.register("communication-methods", CommunicationMethodViewSet)
router.register("billing-methods", BillingViewSet)
router.register("languages", LanguageViewSet)
router.register("banks", BankViewSet)


urlpatterns = router.urls