from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Supplier, ScopeOfWork, SupplierGroup
from .serializers import SupplierSerializer, ScopeOfWorkSerializer, SupplierGroupSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.filter(is_deleted=False).select_related(
        "country", "city", "area", "bank", "scope_of_work"
    ).prefetch_related(
        "supplier_group"
    )
    serializer_class = SupplierSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['supplier_type', 'branch_address', 'supplier_history', 'country', 'city']

    def create(self, request, *args, **kwargs):
        """
        لدعم إنشاء المورد باستخدام multipart/form-data زي العملاء
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()
        return Response(self.get_serializer(supplier).data, status=status.HTTP_201_CREATED)
class ScopeOfWorkViewSet(viewsets.ModelViewSet):
    queryset = ScopeOfWork.objects.all()
    serializer_class = ScopeOfWorkSerializer


class SupplierGroupViewSet(viewsets.ModelViewSet):
    queryset = SupplierGroup.objects.select_related('scope_of_work').all()
    serializer_class = SupplierGroupSerializer
