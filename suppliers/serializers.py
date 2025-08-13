from rest_framework import serializers
from .models import Supplier, ScopeOfWork, SupplierGroup
from shared.serializers import (
    CountrySerializer, CitySerializer, AreaSerializer,
    BankSerializer
)

# ---------- Scope of Work ----------
class ScopeOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeOfWork
        fields = '__all__'


# ---------- Supplier Group ----------
class SupplierGroupSerializer(serializers.ModelSerializer):
    scope_of_work = ScopeOfWorkSerializer(read_only=True)

    class Meta:
        model = SupplierGroup
        fields = '__all__'


# ---------- Supplier ----------
class SupplierSerializer(serializers.ModelSerializer):
    # Read-only nested serializers (للعرض)
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    area = AreaSerializer(read_only=True)
    bank = BankSerializer(read_only=True)
    supplier_group = SupplierGroupSerializer(many=True, read_only=True)
    scope_of_work = ScopeOfWorkSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'
