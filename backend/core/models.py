from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class NameCodeBase(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Name & Code Base"
        verbose_name_plural = "Name & Code Bases"

    def save(self, *args, **kwargs):
        if not self.code:
            prefix = self.__class__.__name__.upper()[:3]  # use model class as prefix
            for _ in range(10):
                unique_part = uuid.uuid4().hex[:6].upper()
                generated_code = f"{prefix}-{unique_part}"
                if not self.__class__.objects.filter(code=generated_code).exists():
                    self.code = generated_code
                    break
            else:
                raise ValueError("\u274c Failed to generate unique code after 10 attempts")
        super().save(*args, **kwargs)

class TrackableBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_updated"
    )
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted"
    )
    is_deleted = models.BooleanField(default=False)
    delete_requested = models.BooleanField(default=False)  # <<-- الحقل الجديد

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        verbose_name = "Trackable Base"
        verbose_name_plural = "Trackable Bases"

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()




class ContactInfoBase(models.Model):
    email = models.EmailField(blank=True, null=True)
    telephone_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    country = models.ForeignKey('shared.Country', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('shared.City', on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey('shared.Area', on_delete=models.SET_NULL, null=True, blank=True)  # ✅ ده المطلوب

    class Meta:
        abstract = True
        verbose_name = "Contact Info"
        verbose_name_plural = "Contact Infos"


class BasePerson(models.Model):
    birth_date = models.DateField(blank=True, null=True)
    home_address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.ForeignKey('shared.Gender', on_delete=models.SET_NULL, null=True, blank=True)
    nationality = models.ForeignKey('shared.Nationality', on_delete=models.SET_NULL, null=True, blank=True)

    national_id_number = models.CharField(max_length=50, blank=True, null=True)
    national_id_attachment = models.FileField(upload_to='national_ids/', blank=True, null=True)
    national_id_expiry_date = models.DateField(blank=True, null=True)

    passport_number = models.CharField(max_length=50, blank=True, null=True)
    passport_attachment = models.FileField(upload_to='passports/', blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)

    signature_attachment = models.FileField(upload_to='signatures/', blank=True, null=True)
    personal_image_attachment = models.ImageField(upload_to='personal_images/', blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Base Person"
        verbose_name_plural = "Base People"


class BaseCompany(models.Model):
    trade_license_number = models.CharField(max_length=50, blank=True, null=True)
    trade_license_expiry_date = models.DateField(blank=True, null=True)
    trade_license_attachment = models.FileField(upload_to='trade_licenses/', blank=True, null=True)

    stamp_attachment = models.ImageField(upload_to='company_stamps/', blank=True, null=True)
    logo_attachment = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    classification = models.ForeignKey('shared.Classification', on_delete=models.SET_NULL, null=True, blank=True)

    postal_code = models.CharField(max_length=10, blank=True, null=True)
    landline_number = models.CharField(max_length=15, blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    map_location = models.URLField(blank=True, null=True)
    establishment_date = models.DateField(blank=True, null=True)
    company_fax = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Base Company"
        verbose_name_plural = "Base Companies"

class BankAccountBase(models.Model):
    bank = models.ForeignKey(
        'shared.Bank',  # ✅ لازم يكون موجود في shared.models
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    iban_number = models.CharField(max_length=50, blank=True, null=True)
    iban_certificate = models.FileField(upload_to='iban_certificates/', blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Bank Account Info"
        verbose_name_plural = "Bank Account Infos"
