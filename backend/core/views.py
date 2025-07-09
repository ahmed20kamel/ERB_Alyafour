from django.utils import timezone
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.contenttypes.models import ContentType
from rest_framework.request import Request

from approvals.models import DeleteClientRequest
from approvals.serializers.approvals.delete_request import DeleteRequestSerializer
from customers.models import Customer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from approvals.mixins import ApprovalMixin

import logging

logger = logging.getLogger(__name__)

ALLOWED_APPROVERS = ["manager", "superadmin", "supervisor"]


class DeleteRequestListCreateAPIView(generics.ListCreateAPIView):
    """
    عرض وإنشاء طلبات الحذف
    """
    queryset = DeleteClientRequest.objects.all().order_by("-created_at")
    serializer_class = DeleteRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "content_type"]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class DeleteRequestApproveRejectAPIView(APIView, ApprovalMixin):
    """
    الموافقة أو رفض طلبات الحذف - للمصرح لهم فقط
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, pk: int) -> Response:
        try:
            delete_request = DeleteClientRequest.objects.get(pk=pk)
        except DeleteClientRequest.DoesNotExist:
            return Response({"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")
        reason = request.data.get("reason", "")

        if not request.user.groups.filter(name__in=ALLOWED_APPROVERS).exists():
            return Response(
                {"detail": "You do not have permission to approve or reject this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        if action == "approve":
            self.approve_request(delete_request, request.user)

            # تطبيق الـ Business Rule: soft delete للعميل
            if delete_request.content_type.model == "customer":
                Customer.objects.filter(pk=delete_request.object_id).update(
                    deleted_at=timezone.now(),
                    delete_requested=False
                )

            self._send_notification(delete_request, "تمت الموافقة", f"تمت الموافقة على حذف العنصر رقم {delete_request.object_id}")

            return Response({"detail": "Request approved successfully."}, status=status.HTTP_200_OK)

        elif action == "reject":
            self.reject_request(delete_request, request.user, reason)

            self._send_notification(delete_request, "تم الرفض", f"تم رفض طلب حذف العنصر رقم {delete_request.object_id}")

            return Response({"detail": "Request rejected successfully."}, status=status.HTTP_200_OK)

        else:
            return Response(
                {"detail": "Invalid action. Use 'approve' or 'reject' only."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _send_notification(self, delete_request, title, message):
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{delete_request.requested_by.id}",
                {
                    "type": "send_notification",
                    "title": title,
                    "message": message,
                }
            )
        except Exception as e:
            logger.warning(f"Notification failed: {e}")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def customers_dashboard_stats(request: Request) -> Response:
    """
    إحصائيات لوحة التحكم للعملاء
    """
    total_customers = Customer.objects.filter(deleted_at__isnull=True).count()

    counts_by_type = (
        Customer.objects
        .filter(deleted_at__isnull=True)
        .values("customer_type")
        .annotate(count=Count("id"))
    )

    counts_dict = {
        "owner": 0,
        "commercial": 0,
        "consultant": 0
    }
    for item in counts_by_type:
        ctype = item["customer_type"] or "unknown"
        counts_dict[ctype] = item["count"]

    recently_added = list(
        Customer.objects.filter(deleted_at__isnull=True)
        .order_by("-created_at")[:5]
        .values("id", "full_name_english", "created_at")
    )

    recently_deleted = list(
        Customer.objects.filter(deleted_at__isnull=False)
        .order_by("-deleted_at")[:5]
        .values("id", "full_name_english", "deleted_at")
    )

    pending_delete_requests = DeleteClientRequest.objects.filter(status="pending").count()

    data = {
        "total_customers": total_customers,
        "counts_by_type": counts_dict,
        "recently_added": recently_added,
        "recently_deleted": recently_deleted,
        "pending_delete_requests": pending_delete_requests,
    }

    return Response(data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_customer_contenttype(request: Request) -> Response:
    """
    جلب content type الخاص بموديل Customer
    """
    try:
        ct = ContentType.objects.get(app_label="customers", model="customer")
        return Response({"id": ct.id})
    except ContentType.DoesNotExist:
        return Response({"detail": "ContentType not found"}, status=status.HTTP_404_NOT_FOUND)
