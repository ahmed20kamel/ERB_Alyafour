from django.db import models
from core.models import (
    NameCodeBase, TrackableBase,
    ContactInfoBase, BankAccountBase,
    BaseCompany, BasePerson,
)

# === Scopes & Groups ===
class ScopeOfWork(NameCodeBase, TrackableBase):
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Scope of Work"
        verbose_name_plural = "Scopes of Work"

    def __str__(self):
        return self.name_en or self.name_ar or super().__str__()


class SupplierGroup(NameCodeBase, TrackableBase):
    scope_of_work = models.ForeignKey(
        ScopeOfWork, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="supplier_groups"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Supplier Group"
        verbose_name_plural = "Supplier Groups"

    def __str__(self):
        return self.name_en or self.name_ar or super().__str__()


# === Supplier ===
class Supplier(NameCodeBase, TrackableBase, ContactInfoBase, BaseCompany, BankAccountBase):
    scope_of_work = models.ForeignKey(
        ScopeOfWork, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="suppliers"
    )
    supplier_groups = models.ManyToManyField(SupplierGroup, related_name="suppliers", blank=True)

    LEGAL_STRUCTURE_CHOICES = [
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('llc', 'Limited Liability Company (LLC)'),
    ]
    legal_structure = models.CharField(max_length=64, blank=True, choices=LEGAL_STRUCTURE_CHOICES)

    trn_number = models.CharField(max_length=100, blank=True)
    vat_certificate = models.FileField(upload_to="supplier_documents/", blank=True, null=True)

    company_website = models.URLField(blank=True, null=True)
    company_mailing_address = models.URLField(blank=True, null=True)
    company_store_location = models.URLField(blank=True, null=True)
    company_pickup_location = models.URLField(blank=True, null=True)

    BRANCH_CHOICES = [
        ('Abu Dhabi', 'Abu Dhabi'), ('Dubai', 'Dubai'), ('Sharjah', 'Sharjah'),
        ('Ajman', 'Ajman'), ('Umm Al Quwain', 'Umm Al Quwain'),
        ('Fujairah', 'Fujairah'), ('Ras Al Khaimah', 'Ras Al Khaimah'),
    ]
    branch_address = models.CharField(max_length=50, blank=True, choices=BRANCH_CHOICES)

    SUPPLIER_HISTORY_CHOICES = [('new', 'New Supplier'), ('previous', 'Previous Supplier')]
    supplier_history = models.CharField(max_length=16, choices=SUPPLIER_HISTORY_CHOICES, default='new')

    SUPPLIER_TYPE_CHOICES = [('supplier', 'Supplier'), ('subcontract', 'Sub Contract')]
    supplier_type = models.CharField(max_length=16, choices=SUPPLIER_TYPE_CHOICES, default='supplier')

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name_en or self.name_ar or super().__str__()


# === Supplier Legal Person (نفس فكرة العملاء) ===
class SupplierLegalPerson(NameCodeBase, TrackableBase, ContactInfoBase, BasePerson):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name="legal_person")
    power_of_attorney_attachment = models.FileField(upload_to="legal/poa/", blank=True, null=True)
    power_of_attorney_expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Supplier Legal Person"
        verbose_name_plural = "Supplier Legal Persons"

    def __str__(self):
        return (self.name_en or self.name_ar) or (self.supplier.name_en or self.supplier.name_ar)


# === Supplier Contact Person (نفس فكرة العملاء) ===
class SupplierContactPerson(NameCodeBase, TrackableBase, ContactInfoBase):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="contact_people")
    job_title = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Supplier Contact Person"
        verbose_name_plural = "Supplier Contact People"

    def __str__(self):
        return (self.name_en or self.name_ar) or (self.supplier.name_en or self.supplier.name_ar)
