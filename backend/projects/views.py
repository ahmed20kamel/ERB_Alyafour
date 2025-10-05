from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, VariationOrder, Payment
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer,
    VariationOrderSerializer, PaymentSerializer
)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related("owner", "consultant").prefetch_related("variation_orders", "payments")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["owner", "consultant", "bank_project_number", "project_code"]
    search_fields = ["project_code", "bank_project_number", "main_contractor", "description"]
    ordering_fields = ["bank_project_number", "project_code"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ProjectDetailSerializer
        return ProjectSerializer

class VariationOrderViewSet(viewsets.ModelViewSet):
    queryset = VariationOrder.objects.select_related("project")
    serializer_class = VariationOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["project", "variation_number", "date"]
    search_fields = ["variation_number", "note"]
    ordering_fields = ["date", "amount"]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("project")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["project", "source", "date"]
    search_fields = ["description"]
    ordering_fields = ["date", "amount"]
