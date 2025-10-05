from rest_framework import serializers
from .models import Project, VariationOrder, Payment

# --- children ---
class VariationOrderSerializer(serializers.ModelSerializer):
    consultant_fee_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    class Meta:
        model = VariationOrder
        fields = [
            "id", "project", "variation_number", "date", "amount",
            "consultant_fee_percentage", "consultant_fee_amount", "note",
        ]
        read_only_fields = ("id", "consultant_fee_amount")

class PaymentSerializer(serializers.ModelSerializer):
    source_display = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "project", "date", "amount", "source", "source_display", "description"]
        read_only_fields = ("id", "source_display")

# --- parent ---
class ProjectSerializer(serializers.ModelSerializer):
    """للإنشاء/التعديل + تعرض المدخلات كما هي"""
    class Meta:
        model = Project
        fields = [
            "id",
            # basic
            "bank_project_number", "project_code", "owner", "consultant",
            "main_contractor", "description",
            "report_as_of", "engineering_auditor", "engineering_audit_date",
            "accounting_auditor", "accounting_audit_date", "notes",
            # finance+duration
            "first_funding_agency", "second_funding_agency",
            "start_order_date", "contract_duration_months", "total_time_extension_days",
            # global contract
            "base_contract_value", "completion_percentage", "consultant_percentage",
            # bank
            "bank_total_financing_value", "bank_completion_percentage", "bank_consultant_percentage",
            # owner
            "owner_completion_percentage", "owner_consultant_percentage",
        ]
        read_only_fields = ("id",)

class ProjectDetailSerializer(ProjectSerializer):
    """تعرض كل المشتقات + الأطفال + المجاميع"""
    # duration
    final_duration_months = serializers.IntegerField(read_only=True)
    end_date_with_extension = serializers.DateField(read_only=True)

    # derived money
    actual_contract_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    consultant_fee_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_contract_incl_consultant_fees = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    bank_actual_contract_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    bank_consultant_fee_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    bank_share_incl_consultant = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    owner_total_financing_value = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    owner_actual_contract_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    owner_consultant_fee_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    owner_share_incl_consultant = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    # VAT sections exposed as {vat, total_incl_vat}
    vat_bank_share_incl_consultant = serializers.SerializerMethodField()
    vat_owner_share_incl_consultant = serializers.SerializerMethodField()
    vat_total_contract_incl_consultant = serializers.SerializerMethodField()
    vat_bank_consultant_fee = serializers.SerializerMethodField()
    vat_owner_consultant_fee = serializers.SerializerMethodField()
    vat_total_consultant_fee = serializers.SerializerMethodField()
    vat_owner_actual_contract = serializers.SerializerMethodField()
    vat_bank_actual_contract = serializers.SerializerMethodField()
    vat_total_actual_contract = serializers.SerializerMethodField()

    # children
    variation_orders = VariationOrderSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    # aggregates
    variations_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    variations_total_consultant_fees = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    payments_total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            # duration
            "final_duration_months", "end_date_with_extension",
            # derived money
            "actual_contract_amount", "consultant_fee_amount", "total_contract_incl_consultant_fees",
            "bank_actual_contract_amount", "bank_consultant_fee_amount", "bank_share_incl_consultant",
            "owner_total_financing_value", "owner_actual_contract_amount",
            "owner_consultant_fee_amount", "owner_share_incl_consultant",
            # VAT
            "vat_bank_share_incl_consultant", "vat_owner_share_incl_consultant", "vat_total_contract_incl_consultant",
            "vat_bank_consultant_fee", "vat_owner_consultant_fee", "vat_total_consultant_fee",
            "vat_owner_actual_contract", "vat_bank_actual_contract", "vat_total_actual_contract",
            # children + totals
            "variation_orders", "payments",
            "variations_total_amount", "variations_total_consultant_fees", "payments_total_amount",
        ]

    # helpers to convert (vat, gross) -> dict
    def _vat_dict(self, tup):
        if not tup or tup[0] is None:
            return {"vat": None, "total_incl_vat": None}
        return {"vat": tup[0], "total_incl_vat": tup[1]}

    def get_vat_bank_share_incl_consultant(self, obj): return self._vat_dict(obj.vat_bank_share_incl_consultant)
    def get_vat_owner_share_incl_consultant(self, obj): return self._vat_dict(obj.vat_owner_share_incl_consultant)
    def get_vat_total_contract_incl_consultant(self, obj): return self._vat_dict(obj.vat_total_contract_incl_consultant)
    def get_vat_bank_consultant_fee(self, obj): return self._vat_dict(obj.vat_bank_consultant_fee)
    def get_vat_owner_consultant_fee(self, obj): return self._vat_dict(obj.vat_owner_consultant_fee)
    def get_vat_total_consultant_fee(self, obj): return self._vat_dict(obj.vat_total_consultant_fee)
    def get_vat_owner_actual_contract(self, obj): return self._vat_dict(obj.vat_owner_actual_contract)
    def get_vat_bank_actual_contract(self, obj): return self._vat_dict(obj.vat_bank_actual_contract)
    def get_vat_total_actual_contract(self, obj): return self._vat_dict(obj.vat_total_actual_contract)
