from django.contrib import admin
from .models import (
    Supplier, SupplierGroup, ScopeOfWork,
    SupplierContactPerson, SupplierLegalPerson
)

class SupplierContactPersonInline(admin.StackedInline):
    model = SupplierContactPerson
    extra = 1

class SupplierLegalPersonInline(admin.StackedInline):
    model = SupplierLegalPerson
    extra = 0
    max_num = 1
    can_delete = True

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("code", "name_en", "name_ar", "supplier_type", "is_active")
    list_filter = ("supplier_type", "is_active", "supplier_history", "branch_address")
    search_fields = ("code", "name_en", "name_ar", "trn_number")
    inlines = [SupplierLegalPersonInline, SupplierContactPersonInline]

@admin.register(SupplierGroup)
class SupplierGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "name_en", "name_ar", "is_active")
    search_fields = ("code", "name_en", "name_ar")

@admin.register(ScopeOfWork)
class ScopeOfWorkAdmin(admin.ModelAdmin):
    list_display = ("code", "name_en", "name_ar")
    search_fields = ("code", "name_en", "name_ar")
