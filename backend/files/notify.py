# files/notify.py
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

SITE_BASE_URL = getattr(settings, "SITE_BASE_URL", "http://localhost:8000")
DEFAULT_WINDOWS = getattr(
    settings, "DEFAULT_REMINDER_WINDOWS", [14, 7, 3, 1, 0])


def _recipients_for(doc):
    if doc.owner_email:
        return [doc.owner_email]
    return getattr(settings, "NOTIFY_FALLBACK_EMAILS", [])


def should_notify(doc):
    """نذكّر فقط عندما days_left يساوي نافذة (0 أو 1/3/7/14 أو alert_window_days). الأيام السالبة لا تُرسَل هنا."""
    d = doc.days_to_expiry
    if d < 0:
        return False
    windows = set(DEFAULT_WINDOWS + [doc.alert_window_days])
    return d in windows


def _build_subject_body(doc):
    d = doc.days_to_expiry
    brand = getattr(settings, "BRAND_NAME", "Documents")
    when = f"EXPIRED on {doc.expires_on}" if d < 0 else f"in {d} day(s) on {doc.expires_on}"
    subject = f"[{brand}] '{doc.title}' expires {when}"
    body = (
        f"Title: {doc.title}\n"
        f"Category: {doc.category or '—'}\n"
        f"Expires on: {doc.expires_on} ({'expired' if d < 0 else f'in {d} day(s)'})\n"
        f"Notes: {doc.notes or '—'}\n"
        f"\nOpen: {SITE_BASE_URL}/files/{doc.pk}/\n"
    )
    return subject, body


def send_notification(doc, *, force=False):
    """
    يرسل مرة واحدة كحد أقصى في اليوم.
    لا يستخدم instance.save() حتى لا يشغّل post_save signal.
    """
    from .models import Document
    today = timezone.localdate()

    # لا تكرار في نفس اليوم إطلاقًا
    if doc.last_notified_on == today:
        return False

    # في الوضع العادي نلتزم بالنوافذ؛ في force (إنشاء/تعديل) نسمح
    if not force and not should_notify(doc):
        return False

    recipients = _recipients_for(doc)
    if not recipients:
        return False

    subject, body = _build_subject_body(doc)
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
              recipients, fail_silently=False)

    # حدّث بدون إشعال signals
    Document.objects.filter(pk=doc.pk).update(last_notified_on=today)
    doc.last_notified_on = today
    return True
