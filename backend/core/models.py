from django.db import models

# ----- النظام الأساسي -----

class StatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ----- الجداول العامة -----

class Country(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class City(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Nationality(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"

    def __str__(self):
        return self.name


class Currency(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name


class CommunicationMethod(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Communication Method"
        verbose_name_plural = "Communication Methods"

    def __str__(self):
        return self.name


class Billing(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Billing"
        verbose_name_plural = "Billings"

    def __str__(self):
        return self.name


class Classification(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"

    def __str__(self):
        return self.name


class Gender(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gender"
        verbose_name_plural = "Genders"

    def __str__(self):
        return self.name

# ----- البيز موديلز -----

class PersonBase(TimeStampedModel):
    birth_date = models.DateField(null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True, blank=True)
    national_id_number = models.CharField(max_length=50, blank=True, null=True)
    national_id_expiry_date = models.DateField(blank=True, null=True)
    national_id_attachment = models.FileField(upload_to='national_ids/', blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    passport_attachment = models.FileField(upload_to='passports/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        abstract = True



class CompanyBase(TimeStampedModel):
    name = models.CharField(max_length=255)
    classification = models.ForeignKey(Classification, on_delete=models.SET_NULL, null=True, blank=True)
    trade_license_number = models.CharField(max_length=50, blank=True, null=True)
    trade_license_expiry_date = models.DateField(blank=True, null=True)
    trade_license_attachment = models.FileField(upload_to='trade_licenses/', blank=True, null=True)
    establishment_date = models.DateField(blank=True, null=True)
    company_stamp_attachment = models.ImageField(upload_to='company_stamps/', blank=True, null=True)
    company_logo_attachment = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    landline_number = models.CharField(max_length=15, blank=True, null=True)
    map_location = models.URLField(blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True
