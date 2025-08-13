from django.contrib import admin
from django import forms
from customers.models import (
    Customer, Person, Company,
    AuthorizedPerson, LegalPerson, ContactPerson
)


# ========== Custom Admin Form ==========
class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

    class Media:
        js = ("admin/js/customer_type_toggle.js",)


# ========== Inlines ==========
class PersonInline(admin.StackedInline):
    model = Person
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name_plural = "Owner Info (for owner only)"
    classes = ["collapse"]
    fieldset_classes = ["collapse"]
    template = 'admin/edit_inline/stacked.html'


class CompanyInline(admin.StackedInline):
    model = Company
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name_plural = "Company Info (for commercial/consultant)"
    classes = ["collapse"]
    template = 'admin/edit_inline/stacked.html'


class AuthorizedPersonInline(admin.StackedInline):
    model = AuthorizedPerson
    extra = 1
    verbose_name_plural = "Authorized Persons (for owner only)"
    classes = ["collapse"]
    template = 'admin/edit_inline/stacked.html'


class LegalPersonInline(admin.StackedInline):
    model = LegalPerson
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name_plural = "Legal Person (for company only)"
    classes = ["collapse"]
    template = 'admin/edit_inline/stacked.html'


class ContactPersonInline(admin.StackedInline):
    model = ContactPerson
    extra = 1
    verbose_name_plural = "Contact Persons (for company only)"
    classes = ["collapse"]
    template = 'admin/edit_inline/stacked.html'


# ========== Customer Admin ==========
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm

    list_display = ["code", "name_en", "customer_type", "status"]
    readonly_fields = ["code", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "customer_type", "name_ar", "name_en", "status", "notes"
            )
        }),
        ("Contact Info", {
            "fields": (
                "email", "telephone_number", "whatsapp_number", "country", "city", "area"
            )
        }),
        ("Bank Info", {
            "fields": (
                "bank", "account_holder_name", "account_number", "iban_number", "iban_certificate"
            )
        }),
        
    
    )

    inlines = [
        PersonInline,
        CompanyInline,
        AuthorizedPersonInline,
        LegalPersonInline,
        ContactPersonInline
    ]
