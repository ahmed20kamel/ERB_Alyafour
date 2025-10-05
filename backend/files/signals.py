# files/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Document
from .notify import send_notification, should_notify


@receiver(post_save, sender=Document)
def notify_on_create_or_update(sender, instance: Document, created, **kwargs):
    today = timezone.localdate()
    d = instance.days_to_expiry

    if created:
        # (1) اتضاف منتهي  أو (2) اتضاف داخل نافذة التبليغ
        if d <= 0 or d <= instance.alert_window_days:
            send_notification(instance, force=True)
        return

    # تحديث: (1) بقى منتهي النهاردة ولم يُخطر اليوم
    if d <= 0 and instance.last_notified_on != today:
        send_notification(instance, force=True)
        return

    # (2) دخل نافذة التذكير القياسية أو alert_window_days
    if should_notify(instance) or (d <= instance.alert_window_days):
        send_notification(instance, force=True)
