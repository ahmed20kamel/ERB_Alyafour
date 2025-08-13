from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class BaseApproval(models.Model):
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_requested"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_approved"
    )
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )
    comment = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(class)s_content_type"
    )
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DeleteClientRequest(BaseApproval):
    class Meta:
        verbose_name = "Delete Client Request"
        verbose_name_plural = "Delete Client Requests"

    def __str__(self):
        return f"Delete Request for {self.target} - Status: {self.status}"

    def approve(self, approver):
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Request already processed.")

        self.status = ApprovalStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()

        if hasattr(self.target, 'soft_delete'):
            self.target.soft_delete(deleted_by=approver)
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

    class Meta:
        verbose_name = "Update Request"
        verbose_name_plural = "Update Requests"

    def __str__(self):
        return f"Update Request for {self.target} - Status: {self.status}"

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
