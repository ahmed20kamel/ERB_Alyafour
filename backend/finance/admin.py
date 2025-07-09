from django.contrib import admin
from finance.models import Bank, BankAccount


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'swift_code', 'country']
    search_fields = ['name', 'swift_code']
    fields = [field.name for field in Bank._meta.fields]


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['bank', 'account_holder_name', 'account_number', 'iban_number']
    search_fields = ['account_holder_name', 'account_number', 'iban_number']
    list_filter = ['bank']
    fields = [field.name for field in BankAccount._meta.fields]
