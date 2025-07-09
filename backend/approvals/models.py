from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

User = get_user_model()

class ApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class BaseApproval(models.Model):
    requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_requested"
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_approved"
    )
    status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )
    comment = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="%(class)s_content_type")
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# ✅ عدلنا الاسم هنا حسب الطلب
class DeleteClientRequest(BaseApproval):
    def approve(self, approver):
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Request already processed.")
        self.status = ApprovalStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()

        if hasattr(self.target, 'deleted_at'):
            self.target.deleted_at = timezone.now()
            self.target.save()
        else:
            self.target.delete()

        self.save()

    def reject(self, approver, comment=None):
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Request already processed.")
        self.status = ApprovalStatus.REJECTED
        self.approved_by = approver
        self.comment = comment
        self.approved_at = timezone.now()
        self.save()


class UpdateRequest(BaseApproval):
    old_data = models.JSONField()
    new_data = models.JSONField()

    def approve(self, approver):
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Request already processed.")
        self.status = ApprovalStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()

        for field, value in self.new_data.items():
            setattr(self.target, field, value)
        self.target.save()

        self.save()

    def reject(self, approver, comment=None):
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Request already processed.")
        self.status = ApprovalStatus.REJECTED
        self.approved_by = approver
        self.comment = comment
        self.approved_at = timezone.now()
        self.save()
