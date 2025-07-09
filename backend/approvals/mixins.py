# core/mixins.py
from django.utils import timezone

class ApprovalMixin:
    def approve_request(self, delete_request, user):
        delete_request.status = "approved"
        delete_request.approved_by = user
        delete_request.approved_at = timezone.now()
        delete_request.save()
        return delete_request

    def reject_request(self, delete_request, user, reason=None):
        delete_request.status = "rejected"
        delete_request.reason = reason
        delete_request.approved_by = user
        delete_request.approved_at = timezone.now()
        delete_request.save()
        return delete_request
