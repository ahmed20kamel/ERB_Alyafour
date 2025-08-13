from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import (
    Supplier, SupplierGroup, ScopeOfWork,
    SupplierContactPerson, SupplierLegalPerson
)
from .serializers import (
    SupplierSerializer, SupplierGroupSerializer, ScopeOfWorkSerializer,
    SupplierContactPersonSerializer, SupplierLegalPersonSerializer
)

class ScopeOfWorkViewSet(viewsets.ModelViewSet):
    queryset = ScopeOfWork.objects.all()
    serializer_class = ScopeOfWorkSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierGroupViewSet(viewsets.ModelViewSet):
    queryset = SupplierGroup.objects.select_related("scope_of_work")
    serializer_class = SupplierGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.select_related(
        "country","city","area","bank","classification"
    ).prefetch_related("supplier_groups","contact_people")
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierContactPersonViewSet(viewsets.ModelViewSet):
    queryset = SupplierContactPerson.objects.select_related("supplier")
    serializer_class = SupplierContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierLegalPersonViewSet(viewsets.ModelViewSet):
    queryset = SupplierLegalPerson.objects.select_related("supplier")
    serializer_class = SupplierLegalPersonSerializer
    permission_classes = [permissions.IsAuthenticated]
