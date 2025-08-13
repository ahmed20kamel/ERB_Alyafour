from django.test import TestCase

# Create your tests here.
from django.urls import path
from .views import SupplierViewSet

urlpatterns = [
    path("suppliers/", SupplierViewSet.as_view({'get': 'list'})),  # كمثال
]
