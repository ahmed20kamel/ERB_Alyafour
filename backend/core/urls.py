from django.urls import path
from .views import (
    DeleteRequestListCreateAPIView,
    DeleteRequestApproveRejectAPIView,
    customers_dashboard_stats,
    get_customer_contenttype,
)

urlpatterns = [
    path(
        "delete-requests/",
        DeleteRequestListCreateAPIView.as_view(),
        name="delete-requests-list-create",
    ),
    path(
        "delete-requests/<int:pk>/approve-reject/",
        DeleteRequestApproveRejectAPIView.as_view(),
        name="delete-request-approve-reject",
    ),
    path(
        "customers-dashboard-stats/",
        customers_dashboard_stats,
        name="customers-dashboard-stats",
    ),
    path(
        "customer-contenttype/",
        get_customer_contenttype,
        name="customer-contenttype",
    ),
    
]
