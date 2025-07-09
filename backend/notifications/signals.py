from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from django.contrib.auth import get_user_model
from approvals.models import DeleteClientRequest

from customers.models import Customer

User = get_user_model()

@receiver(post_save, sender=DeleteClientRequest
)
def notify_delete_request(sender, instance, created, **kwargs):
    """
    send notification only if delete request target is Customer
    """
    target = instance.target

    # نتأكد إن المستهدف فعلاً عميل
    if not isinstance(target, Customer):
        return

    if created:
        # ابعت لكل المدراء
        managers = User.objects.filter(groups__name="Manager")
        for manager in managers:
            Notification.objects.create(
                user=manager,
                title="طلب حذف عميل جديد",
                body=f"{instance.requested_by.username} طلب حذف العميل {target.full_name_english}"
            )

    elif instance.status == "approved":
        Notification.objects.create(
            user=instance.requested_by,
            title="تمت الموافقة على حذف العميل",
            body=f"تمت الموافقة على حذف العميل {target.full_name_english}."
        )

    elif instance.status == "rejected":
        Notification.objects.create(
            user=instance.requested_by,
            title="تم رفض طلب حذف العميل",
            body=f"تم رفض حذف العميل {target.full_name_english}. السبب: {instance.reason or 'بدون سبب محدد'}"
        )
