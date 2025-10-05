from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from datetime import timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

TWOPL = Decimal("0.01")
VAT_RATE = Decimal("0.05")  # 5%

class Project(models.Model):
    # ---------- Basic Info (inputs) ----------
    bank_project_number = models.IntegerField(unique=True, verbose_name="Bank Project Number")
    project_code = models.CharField(max_length=100, unique=True, verbose_name="Project Code")

    owner = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        limit_choices_to={"customer_type": "owner"},
        related_name="owned_projects",
        verbose_name="Owner",
    )
    consultant = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        limit_choices_to={"customer_type": "consultant"},
        related_name="consulted_projects",
        verbose_name="Consultant",
    )

    main_contractor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Main Contractor")
    description = models.TextField(blank=True, null=True, verbose_name="Project Description")

    # optional header helpers (كما في الشيت)
    report_as_of = models.DateField(blank=True, null=True, verbose_name="Report As-Of Date")
    engineering_auditor = models.CharField(max_length=255, blank=True, null=True)
    engineering_audit_date = models.DateField(blank=True, null=True)
    accounting_auditor = models.CharField(max_length=255, blank=True, null=True)
    accounting_audit_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # ---------- Finance & Duration (inputs) ----------
    first_funding_agency = models.CharField(max_length=255, blank=True, null=True)
    second_funding_agency = models.CharField(max_length=255, blank=True, null=True)

    start_order_date = models.DateField(blank=True, null=True)
    contract_duration_months = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    total_time_extension_days = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])

    # ---------- Global Contract (inputs) ----------
    # إجمالي قيمة التعاقد بدون أتعاب الاستشاري
    base_contract_value = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]
    )
    completion_percentage = models.DecimalField(  # %
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    consultant_percentage = models.DecimalField(  # %
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ---------- Bank Financing (inputs) ----------
    bank_total_financing_value = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]
    )
    bank_completion_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    bank_consultant_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ---------- Owner Financing (inputs) ----------
    owner_completion_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    owner_consultant_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ---------- Derived (DON'T STORE) ----------
    @property
    def final_duration_months(self):
        if self.contract_duration_months is None or self.total_time_extension_days is None:
            return None
        return self.contract_duration_months + ceil(self.total_time_extension_days / 30)

    @property
    def end_date_with_extension(self):
        if (not self.start_order_date or
            self.contract_duration_months is None or
            self.total_time_extension_days is None):
            return None
        base_end = self.start_order_date + relativedelta(months=self.contract_duration_months)
        return base_end + timedelta(days=self.total_time_extension_days)

    @property
    def actual_contract_amount(self):
        if self.base_contract_value is None:
            return None
        e = (self.completion_percentage or Decimal("0")) / Decimal("100")
        return (self.base_contract_value * e).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def consultant_fee_amount(self):
        actual = self.actual_contract_amount
        if actual is None:
            return None
        b = (self.consultant_percentage or Decimal("0")) / Decimal("100")
        return (actual * b).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def total_contract_incl_consultant_fees(self):
        actual = self.actual_contract_amount
        fee = self.consultant_fee_amount
        if actual is None or fee is None:
            return None
        return (actual + fee).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def bank_actual_contract_amount(self):
        f = self.bank_total_financing_value
        if f is None:
            return None
        e_b = (self.bank_completion_percentage or Decimal("0")) / Decimal("100")
        return (f * e_b).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def bank_consultant_fee_amount(self):
        actual = self.bank_actual_contract_amount
        if actual is None:
            return None
        b_b = (self.bank_consultant_percentage or Decimal("0")) / Decimal("100")
        return (actual * b_b).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def bank_share_incl_consultant(self):
        actual = self.bank_actual_contract_amount
        fee = self.bank_consultant_fee_amount
        if actual is None or fee is None:
            return None
        return (actual + fee).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def owner_total_financing_value(self):
        if self.base_contract_value is None or self.bank_total_financing_value is None:
            return None
        val = self.base_contract_value - self.bank_total_financing_value
        if val < 0:
            val = Decimal("0.00")
        return val.quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def owner_actual_contract_amount(self):
        f = self.owner_total_financing_value
        if f is None:
            return None
        e_o = (self.owner_completion_percentage or Decimal("0")) / Decimal("100")
        return (f * e_o).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def owner_consultant_fee_amount(self):
        actual = self.owner_actual_contract_amount
        if actual is None:
            return None
        b_o = (self.owner_consultant_percentage or Decimal("0")) / Decimal("100")
        return (actual * b_o).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def owner_share_incl_consultant(self):
        actual = self.owner_actual_contract_amount
        fee = self.owner_consultant_fee_amount
        if actual is None or fee is None:
            return None
        return (actual + fee).quantize(TWOPL, rounding=ROUND_HALF_UP)

    # ---------- VAT helpers ----------
    @staticmethod
    def _vat(amount):
        if amount is None:
            return (None, None)
        vat = (amount * VAT_RATE).quantize(TWOPL, rounding=ROUND_HALF_UP)
        gross = (amount + vat).quantize(TWOPL, rounding=ROUND_HALF_UP)
        return (vat, gross)

    @property
    def vat_bank_share_incl_consultant(self): return self._vat(self.bank_share_incl_consultant)
    @property
    def vat_owner_share_incl_consultant(self): return self._vat(self.owner_share_incl_consultant)
    @property
    def vat_total_contract_incl_consultant(self): return self._vat(self.total_contract_incl_consultant_fees)
    @property
    def vat_bank_consultant_fee(self): return self._vat(self.bank_consultant_fee_amount)
    @property
    def vat_owner_consultant_fee(self): return self._vat(self.owner_consultant_fee_amount)
    @property
    def vat_total_consultant_fee(self): return self._vat(self.consultant_fee_amount)
    @property
    def vat_owner_actual_contract(self): return self._vat(self.owner_actual_contract_amount)
    @property
    def vat_bank_actual_contract(self): return self._vat(self.bank_actual_contract_amount)
    @property
    def vat_total_actual_contract(self): return self._vat(self.actual_contract_amount)

    # ---------- Aggregations from children ----------
    @property
    def variations_total_amount(self):
        qs = getattr(self, "variation_orders", None)
        total = sum((v.amount or Decimal("0.00")) for v in (qs.all() if qs else []))
        return Decimal(total).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def variations_total_consultant_fees(self):
        qs = getattr(self, "variation_orders", None)
        total = sum((v.consultant_fee_amount or Decimal("0.00")) for v in (qs.all() if qs else []))
        return Decimal(total).quantize(TWOPL, rounding=ROUND_HALF_UP)

    @property
    def payments_total_amount(self):
        qs = getattr(self, "payments", None)
        total = sum((p.amount or Decimal("0.00")) for p in (qs.all() if qs else []))
        return Decimal(total).quantize(TWOPL, rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.project_code} / {self.bank_project_number}"

    class Meta:
        ordering = ["-bank_project_number"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class VariationOrder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="variation_orders")
    variation_number = models.CharField(max_length=100)
    date = models.DateField(blank=True, null=True)
    # قد تكون سالبة (خصم)
    amount = models.DecimalField(max_digits=20, decimal_places=2,
                                 validators=[MinValueValidator(Decimal("-999999999999.99"))])
    consultant_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["date", "id"]
        unique_together = [("project", "variation_number")]

    @property
    def consultant_fee_amount(self):
        if self.amount is None:
            return None
        pct = (self.consultant_fee_percentage or Decimal("0")) / Decimal("100")
        return (self.amount * pct).quantize(TWOPL, rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.project.project_code} - {self.variation_number}"


class Payment(models.Model):
    class Source(models.TextChoices):
        CLIENT = "CLIENT", "Client Payment"
        BANK = "BANK", "Bank Payment"
        OTHER = "OTHER", "Other"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)])
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.CLIENT)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["date", "id"]

    def __str__(self):
        return f"{self.project.project_code} - {self.get_source_display()} - {self.amount}"
