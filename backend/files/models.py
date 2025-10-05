from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=20,
        default='secondary',
        help_text='Bootstrap color name: primary, success, warning, danger…'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    owner_email = models.EmailField(
        blank=True,
        help_text='Recipient for expiry alerts (optional).'
    )
    expires_on = models.DateField()
    alert_window_days = models.PositiveIntegerField(
        default=7,
        help_text='Send an alert this many days before expiry.'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # housekeeping for notifications
    last_notified_on = models.DateField(null=True, blank=True)
    # ⬇️ جديد: علشان ما نبعتش تاني لنفس التاريخ/المدة
    last_notified_for_expires_on = models.DateField(null=True, blank=True)
    last_notified_for_offset = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['expires_on', 'title']

    def __str__(self):
        return self.title

    @property
    def days_to_expiry(self):
        today = timezone.localdate()
        return (self.expires_on - today).days

    def status(self):
        d = self.days_to_expiry
        if d < 0:
            return ('Expired', 'danger')
        elif d <= 3:
            return ('Expiring soon', 'warning')
        else:
            return ('Active', 'success')
