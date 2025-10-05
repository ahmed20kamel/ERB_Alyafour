from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from datetime import date, timedelta
from files.models import Document

# تقدر تغيّرها من settings لو حابب
DEFAULT_WINDOWS = set(getattr(settings, "DEFAULT_REMINDER_WINDOWS", [14, 7, 3, 1, 0]))
INCLUDE_EXPIRED_DAYS = int(getattr(settings, "INCLUDE_EXPIRED_DAYS", 7))  # ابعت للمنتهي خلال آخر N أيام

def site_url():
    return getattr(settings, "SITE_BASE_URL", "http://localhost:8000").rstrip("/")

def should_notify(doc: Document, today: date, windows=DEFAULT_WINDOWS, include_expired_days=INCLUDE_EXPIRED_DAYS):
    days = (doc.expires_on - today).days
    win = doc.alert_window_days or 7

    # ابعت لو: داخل نافذة التنبيه (قبل الانتهاء) أو في أي من النوافذ المعيارية (±) أو منتهي من N أيام
    due = False
    if -include_expired_days <= days <= win:
        due = True
    if days in windows or (-days) in windows:
        due = True

    # امنع التكرار لنفس الحالة
    if (
        doc.last_notified_for_expires_on == doc.expires_on
        and doc.last_notified_for_offset == days
    ):
        return (False, days)

    return (due, days)

def build_email(doc: Document, days_left: int):
    subject = f"[Expiry Alert] {doc.title} — expires {doc.expires_on}"
    if days_left > 0:
        line = f"This document will expire in {days_left} day(s)."
    elif days_left == 0:
        line = "This document expires today."
    else:
        line = f"This document expired {-days_left} day(s) ago."

    url = f"{site_url()}/app/files/documents/{doc.id}"
    body = (
        f"Title      : {doc.title}\n"
        f"Category   : {doc.category.name if doc.category else '—'}\n"
        f"Expires on : {doc.expires_on}\n"
        f"{line}\n\n"
        f"Open: {url}\n"
    )
    sender = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
    recipient = (doc.owner_email or "").strip()
    fallbacks = getattr(settings, "NOTIFY_FALLBACK_EMAILS", []) or []

    to_list = [recipient] if recipient else []
    for f in fallbacks:
        if f and f not in to_list:
            to_list.append(f)

    return subject, body, sender, to_list

def create_notification(doc: Document, days_left: int, sent_ok: bool):
    try:
        from notifications.models import Notification
    except Exception:
        return
    title = f"Expiry: {doc.title} ({doc.expires_on})"
    if days_left > 0:
        body = f"Expires in {days_left} day(s)."
    elif days_left == 0:
        body = "Expires today."
    else:
        body = f"Expired {-days_left} day(s) ago."
    url = f"/app/files/documents/{doc.id}"
    Notification.objects.create(
        title=title,
        body=body + ("" if sent_ok else " (email failed)"),
        url=url,
        is_read=False,
    )

class Command(BaseCommand):
    help = "Send expiry notifications for documents due/expired (includes recently expired). Prevents duplicates."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print candidates without sending")
        parser.add_argument("--include-expired-days", type=int, default=None, help="Override INCLUDE_EXPIRED_DAYS")

    def handle(self, *args, **opts):
        today = timezone.localdate()
        include_expired_days = opts["include_expired_days"]
        if include_expired_days is None:
            include_expired_days = INCLUDE_EXPIRED_DAYS

        # جيب اللي منتهي من N أيام لغاية اللي لسه قدّامه كتير (فلتر أولي واسع)
        qs = Document.objects.filter(
            expires_on__gte=today - timedelta(days=include_expired_days)
        ).order_by("expires_on")

        total, sent = 0, 0
        for doc in qs:
            total += 1
            ok, days = should_notify(doc, today, DEFAULT_WINDOWS, include_expired_days)
            if not ok:
                continue

            subject, body, sender, to_list = build_email(doc, days)
            # حتى لو مفيش بريد، نسجل Notification جوّه السيستم
            if not to_list:
                create_notification(doc, days, sent_ok=False)
                continue

            if opts["dry_run"]:
                self.stdout.write(f"[DRY] {doc.id} -> {to_list} : {subject}")
                continue

            try:
                cnt = send_mail(subject, body, sender, to_list)
                sent += cnt
                doc.last_notified_on = today
                doc.last_notified_for_expires_on = doc.expires_on
                doc.last_notified_for_offset = days
                doc.save(update_fields=[
                    "last_notified_on",
                    "last_notified_for_expires_on",
                    "last_notified_for_offset",
                    "updated_at",
                ])
                create_notification(doc, days, sent_ok=cnt > 0)
            except Exception as e:
                self.stderr.write(f"[ERR] doc={doc.id} email failed: {e}")
                create_notification(doc, days, sent_ok=False)

        self.stdout.write(f"Checked: {total} | Notifications sent: {sent}")
