from django.contrib import admin
from .models import Project, VariationOrder, Payment

class VariationOrderInline(admin.TabularInline):
    model = VariationOrder
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_code", "bank_project_number",
        "owner", "consultant",
        "base_contract_value", "completion_percentage",
    )
    search_fields = ("project_code", "bank_project_number", "main_contractor", "description")
    list_filter = ("owner", "consultant")
    inlines = [VariationOrderInline, PaymentInline]

    readonly_fields = (
        # Duration
        "final_duration_months", "end_date_with_extension",
        # Global contract derived
        "actual_contract_amount", "consultant_fee_amount", "total_contract_incl_consultant_fees",
        # Bank derived
        "bank_actual_contract_amount", "bank_consultant_fee_amount", "bank_share_incl_consultant",
        # Owner derived
        "owner_total_financing_value", "owner_actual_contract_amount",
        "owner_consultant_fee_amount", "owner_share_incl_consultant",
        # Totals from children
        "variations_total_amount", "variations_total_consultant_fees", "payments_total_amount",
    )

@admin.register(VariationOrder)
class VariationOrderAdmin(admin.ModelAdmin):
    list_display = ("project", "variation_number", "date", "amount",
                    "consultant_fee_percentage", "consultant_fee_amount")
    search_fields = ("variation_number",)
    list_filter = ("project",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("project", "date", "amount", "source", "description")
    search_fields = ("description",)
    list_filter = ("project", "source")
