from django.db import models
from django.utils import timezone
from core.models import (
    Country, City, Currency, CommunicationMethod, Billing, Classification,
    PersonBase, CompanyBase
)
import uuid


class Customer(PersonBase):
    CUSTOMER_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('commercial', 'Commercial'),
        ('consultant', 'Consultant'),
    ]

    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES)
    customer_code = models.CharField(max_length=50, unique=True, blank=True)

    full_name_arabic = models.CharField(max_length=255)
    full_name_english = models.CharField(max_length=255)
    email = models.EmailField()
    telephone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    communication_method = models.ForeignKey(CommunicationMethod, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    billing = models.ForeignKey(Billing, on_delete=models.SET_NULL, null=True, blank=True)

    preferred_language = models.CharField(
        max_length=10,
        choices=[("en", "English"), ("ar", "Arabic")],
        default="en"
    )
    status = models.CharField(max_length=20, default='active')

    deleted_at = models.DateTimeField(null=True, blank=True)
    delete_requested = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(PersonBase.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["national_id_number", "nationality"],
                name="unique_customer_national_id_per_nationality"
            )
        ]

    def __str__(self):
        return self.full_name_english

    def save(self, *args, **kwargs):
        if not self.customer_code:
            prefix = {
                'owner': 'OWN',
                'commercial': 'COM',
                'consultant': 'CON',
            }.get(self.customer_type, 'CUS')

            while True:
                unique_part = uuid.uuid4().hex[:6].upper()
                code = f"{prefix}-{unique_part}"
                if not Customer.objects.filter(customer_code=code).exists():
                    self.customer_code = code
                    break

        super().save(*args, **kwargs)


class OwnerProfile(PersonBase):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='owner_profile')

    signature_attachment = models.ImageField(upload_to='owner/signatures/', blank=True, null=True)
    personal_image_attachment = models.ImageField(upload_to='owner/personal_images/', blank=True, null=True)
    passport_attachment = models.FileField(upload_to='owner/passports/', blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)

    authorized_person_name = models.CharField(max_length=100, blank=True, null=True)
    authorized_person_email = models.EmailField(blank=True, null=True)
    authorized_person_phone_number = models.CharField(max_length=15, blank=True, null=True)
    authorized_person_birth_date = models.DateField(blank=True, null=True)
    authorized_person_address = models.CharField(max_length=255, blank=True, null=True)
    authorized_person_national_id_number = models.CharField(max_length=50, blank=True, null=True)
    authorized_person_national_id_expiry_date = models.DateField(blank=True, null=True)
    authorized_person_national_id_attachment = models.FileField(upload_to='authorized/national_ids/', blank=True, null=True)
    authorized_person_passport_number = models.CharField(max_length=50, blank=True, null=True)
    authorized_person_passport_expiry_date = models.DateField(blank=True, null=True)
    authorized_person_passport_attachment = models.FileField(upload_to='authorized/passports/', blank=True, null=True)
    authorized_person_power_of_attorney_attachment = models.FileField(upload_to='authorized/poa/', blank=True, null=True)
    authorized_person_power_of_attorney_expiry_date = models.DateField(blank=True, null=True)
    authorized_person_signature_attachment = models.ImageField(upload_to='authorized/signatures/', blank=True, null=True)
    authorized_person_personal_image_attachment = models.ImageField(upload_to='authorized/personal_images/', blank=True, null=True)

    class Meta(PersonBase.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["national_id_number", "nationality"],
                name="unique_ownerprofile_national_id_per_nationality"
            )
        ]

    def __str__(self):
        return self.full_name


class CompanyProfile(CompanyBase):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='company_profile')

    postal_code = models.CharField(max_length=10, blank=True, null=True)
    landline_number = models.CharField(max_length=15, blank=True, null=True)
    company_office_address = models.TextField(blank=True, null=True)
    company_logo_attachment = models.ImageField(upload_to='company/logos/', blank=True, null=True)
    company_trade_license_attachment = models.ImageField(upload_to='company/licenses/', blank=True, null=True)
    company_trade_license_number = models.CharField(max_length=50, blank=True, null=True)
    company_trade_license_expiry_date = models.DateField(blank=True, null=True)
    company_stamp_attachment = models.ImageField(upload_to='company/stamps/', blank=True, null=True)
    company_establishment_date = models.DateField(blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    map_location = models.URLField(blank=True, null=True)
    classification = models.ForeignKey(Classification, on_delete=models.SET_NULL, null=True, blank=True)

    responsible_person_name = models.CharField(max_length=100, blank=True, null=True)
    responsible_person_birth_date = models.DateField(blank=True, null=True)
    responsible_person_address = models.CharField(max_length=255, blank=True, null=True)
    responsible_person_job_title = models.CharField(max_length=100, blank=True, null=True)
    responsible_person_email = models.EmailField(blank=True, null=True)
    responsible_person_phone_number = models.CharField(max_length=15, blank=True, null=True)
    responsible_person_national_id_number = models.CharField(max_length=50, blank=True, null=True)
    responsible_person_national_id_expiry_date = models.DateField(blank=True, null=True)
    responsible_person_national_id_attachment = models.FileField(upload_to='company/responsible_ids/', blank=True, null=True)
    responsible_person_passport_number = models.CharField(max_length=50, blank=True, null=True)
    responsible_person_passport_expiry_date = models.DateField(blank=True, null=True)
    responsible_person_passport_attachment = models.FileField(upload_to='company/responsible_passports/', blank=True, null=True)
    responsible_person_power_of_attorney_attachment = models.FileField(upload_to='company/responsible_poa/', blank=True, null=True)
    responsible_person_power_of_attorney_expiry_date = models.DateField(blank=True, null=True)
    responsible_person_signature_attachment = models.ImageField(upload_to='company/responsible_signatures/', blank=True, null=True)
    responsible_person_personal_image_attachment = models.ImageField(upload_to='company/responsible_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class ContactPerson(models.Model):
    company_profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='contact_people'
    )
    name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.name
