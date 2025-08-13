from django.db import models
from core.models import (
    NameCodeBase,
    TrackableBase,
    ContactInfoBase,
    BankAccountBase,
    BaseCompany  # ✅ الكلاس الصحيح بدل BaseCompanyFieldsMixin
)


class ScopeOfWork(models.Model):
    name = models.CharField(unique=True, verbose_name="Scope of Work", max_length=255)
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return self.name


class SupplierGroup(models.Model):
    name = models.CharField(unique=True, verbose_name="Supplier Group", max_length=255)
    scope_of_work = models.ForeignKey(ScopeOfWork, on_delete=models.CASCADE, related_name='supplier_groups')

    def __str__(self):
        return self.name


class Supplier(
    NameCodeBase,
    TrackableBase,
    ContactInfoBase,
    BankAccountBase,
    BaseCompany,  # ✅ تم التعديل هنا
):
    # روابط وتصنيفات
    scope_of_work = models.ForeignKey(
        ScopeOfWork,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suppliers'
    )

    supplier_group = models.ManyToManyField(
        SupplierGroup,
        related_name='suppliers',
        verbose_name="Supplier Groups"
    )

    # روابط خارجية
    company_website = models.URLField(verbose_name="Website", blank=True, null=True, max_length=512)
    company_mailing_address = models.URLField(verbose_name="Mailing Address", blank=True, null=True, max_length=512)
    company_store_location = models.URLField(verbose_name="Store Location (Map Link)", blank=True, null=True, max_length=512)
    company_pickup_location = models.URLField(verbose_name="Pickup Location (Map Link)", blank=True, null=True, max_length=512)

    # وثائق رسمية إضافية
    authority_letter = models.FileField(upload_to='supplier_documents/', verbose_name="Authority Letter", blank=True, null=True)
    ct_certificate = models.FileField(upload_to='supplier_documents/', verbose_name="CT Certificate", blank=True, null=True)
    poa = models.FileField(upload_to='supplier_documents/', verbose_name="POA", blank=True, null=True)

    # هيكل الشركة
    legal_structure = models.CharField(
        choices=[
            ('sole_proprietorship', 'Sole Proprietorship'),
            ('partnership', 'Partnership'),
            ('llc', 'Limited Liability Company (LLC)')
        ],
        verbose_name="Legal Structure",
        blank=True,
        max_length=50
    )

    trn_number = models.CharField(verbose_name="TRN Number", blank=True, max_length=50)

    # عنوان الفرع
    branch_address = models.CharField(
        choices=[
            ('Abu Dhabi', 'Abu Dhabi'),
            ('Dubai', 'Dubai'),
            ('Sharjah', 'Sharjah'),
            ('Ajman', 'Ajman'),
            ('Umm Al Quwain', 'Umm Al Quwain'),
            ('Fujairah', 'Fujairah'),
            ('Ras Al Khaimah', 'Ras Al Khaimah')
        ],
        verbose_name="Branch Address",
        blank=True,
        max_length=50
    )

    # تاريخ المورد
    supplier_history = models.CharField(
        choices=[
            ('new', 'New Supplier'),
            ('previous', 'Previous Supplier')
        ],
        verbose_name="Supplier History",
        default='new',
        max_length=20
    )

    supplier_type = models.CharField(
        choices=[
            ('supplier', 'Supplier'),
            ('subcontract', 'Sub Contract'),
        ],
        default='supplier',
        verbose_name="Supplier Type",
        max_length=20
    )

    def __str__(self):
        return self.name_en or self.name_ar or "Unnamed Supplier"
