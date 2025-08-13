from rest_framework import viewsets
from shared.models import (
    Country, City, Area, Nationality, Gender, Classification,
    Currency, CommunicationMethod, Billing, Language, Bank
)
from shared.serializers import (
    CountrySerializer, CitySerializer, AreaSerializer, NationalitySerializer,
    GenderSerializer, ClassificationSerializer, CurrencySerializer,
    CommunicationMethodSerializer, BillingSerializer,LanguageSerializer, BankSerializer
)

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer

from django_filters.rest_framework import DjangoFilterBackend  # ⬅️ فوق لو مش مضاف

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']  # ← هنا بنفعل الفلترة بالبلد

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Area.objects.filter(is_active=True)
    serializer_class = AreaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city']  # ← هنا بنفعل الفلترة بالمدينة


class NationalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Nationality.objects.filter(is_active=True)
    serializer_class = NationalitySerializer

class GenderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gender.objects.filter(is_active=True)
    serializer_class = GenderSerializer

class ClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Classification.objects.filter(is_active=True)
    serializer_class = ClassificationSerializer

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer

class CommunicationMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationMethod.objects.filter(is_active=True)
    serializer_class = CommunicationMethodSerializer

class BillingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Billing.objects.filter(is_active=True)
    serializer_class = BillingSerializer
class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer

class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.filter(is_active=True)
    serializer_class = BankSerializer
    