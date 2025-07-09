from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from customers.models import Customer
from .owner_profile import OwnerProfileSerializer
from .company_profile import CompanyProfileSerializer
from core.serializers.lookups import (
    CountrySerializer, CitySerializer, CurrencySerializer,
    CommunicationMethodSerializer, BillingSerializer
)
from finance.serializers import BankAccountSerializer
from core.models import Country, City, Currency, CommunicationMethod, Billing


class CustomerSerializer(WritableNestedModelSerializer):
    # Nested profiles
    owner_profile = OwnerProfileSerializer(required=False)
    company_profile = CompanyProfileSerializer(required=False)

    # Read-only nested objects
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    communication_method = CommunicationMethodSerializer(read_only=True)
    billing = BillingSerializer(read_only=True)
    bank_account = BankAccountSerializer(read_only=True)

    # Writable foreign key IDs
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source="country", write_only=True, required=False)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source="city", write_only=True, required=False)
    currency_id = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all(), source="currency", write_only=True, required=False)
    communication_method_id = serializers.PrimaryKeyRelatedField(queryset=CommunicationMethod.objects.all(), source="communication_method", write_only=True, required=False)
    billing_id = serializers.PrimaryKeyRelatedField(queryset=Billing.objects.all(), source="billing", write_only=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_type',
            'customer_code',
            'full_name_arabic',
            'full_name_english',
            'email',
            'telephone_number',
            'whatsapp_number',
            'notes',
            'status',
            'delete_requested',
            'deleted_at',
            'created_at',
            'updated_at',

            # Read-only nested
            'country', 'city', 'currency', 'communication_method', 'billing', 'bank_account',

            # Write-only foreign keys
            'country_id', 'city_id', 'currency_id', 'communication_method_id', 'billing_id',

            # Profiles
            'owner_profile',
            'company_profile',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_code']
