# suppliers/admin.py
from django.contrib import admin
from .models import (
    SupplierGroup, PaymentTerm, Supplier,
    SupplierAddress, SupplierContactPerson, SupplierDocument, SupplierRating
)

class SupplierAddressInline(admin.TabularInline):
    model = SupplierAddress
    fk_name = "supplier"      # ← مهم
    extra = 0

class SupplierContactInline(admin.TabularInline):
    model = SupplierContactPerson
    fk_name = "supplier"      # ← مهم
    extra = 0

class SupplierDocumentInline(admin.TabularInline):
    model = SupplierDocument
    fk_name = "supplier"      # ← مهم
    extra = 0

class SupplierRatingInline(admin.TabularInline):
    model = SupplierRating
    fk_name = "supplier"      # ← مهم
    extra = 0

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    # ...
    inlines = [SupplierAddressInline, SupplierContactInline, SupplierDocumentInline, SupplierRatingInline]
