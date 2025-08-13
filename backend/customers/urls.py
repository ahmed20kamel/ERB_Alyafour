from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from customers.views import (
    CustomerViewSet,
    PersonViewSet,
    CompanyViewSet,
    AuthorizedPersonViewSet,
    ContactPersonViewSet,
    LegalPersonViewSet,
    customer_dashboard_stats,
)

# Routers
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'persons', PersonViewSet, basename='person')
router.register(r'companies', CompanyViewSet, basename='company')

# Nested routes
customers_router = NestedDefaultRouter(router, r'customers', lookup='customer')
customers_router.register(r'authorized-people', AuthorizedPersonViewSet, basename='customer-authorized-people')
customers_router.register(r'contact-people', ContactPersonViewSet, basename='customer-contact-people')
customers_router.register(r'legal-persons', LegalPersonViewSet, basename='customer-legal-persons')

# Final urlpatterns
urlpatterns = [
    path('customers/dashboard-stats/', customer_dashboard_stats),
    path('', include(router.urls)),
    path('', include(customers_router.urls)),

    # ✅ ثابت - ده هيشتغل على /api/customers/dashboard-stats/
    
]
