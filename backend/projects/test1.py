from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from datetime import timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

TWOPL = Decimal("0.01")
VAT_RATE = Decimal("0.05")  # 5%

class Project(models.Model):
    # ---------- Basic Info ----------
    project_number_fab = models.CharField(max_length=100, unique=True, verbose_name="رقم المشروع البنك")
    project_code = models.CharField(max_length=50, verbose_name="كود المشروع")

    # Parties
    owner = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        limit_choices_to={"customer_type": "owner"},
        related_name="owned_projects",
        verbose_name="المالك",
    )
    consultant = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        limit_choices_to={"customer_type": "consultant"},
        related_name="consulted_projects",
        verbose_name="الاستشاري",
    )
    main_contractor = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        limit_choices_to={"customer_type": "commercial"},
        related_name="contracted_projects",
        verbose_name="المقاول الرئيسي",
    )

    # Description & Finance Orgs
    description = models.TextField(blank=True, null=True, verbose_name="وصف المشروع")
    first_finance  = models.CharField(max_length=255, blank=True, null=True, verbose_name="جهة التمويل الأولى")
    second_finance = models.CharField(max_length=255, blank=True, null=True, verbose_name="جهة التمويل الثانية")

    # Dates & Durations (inputs)
    start_date = models.DateField(blank=True, null=True, verbose_name="تاريخ أمر المباشرة")
    duration_months = models.PositiveIntegerField(default=0, verbose_name="مدة المشروع (شهور)")
    time_extension_days = models.PositiveIntegerField(default=0, verbose_name="مجموع التمديد الزمني (أيام)")

    # Derived (stored)
    final_duration_months = models.PositiveIntegerField(default=0, verbose_name="المدة النهائية للمشروع (شهور)")
    end_date_with_extension = models.DateField(blank=True, null=True, verbose_name="تاريخ نهاية المشروع مع التمديد")

    # Contract & Percentages (inputs)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"),validators=[MinValueValidator(0)], verbose_name="إجمالي قيمة التعاقد (بدون الاستشاري)")
    consultant_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"),validators=[MinValueValidator(0), MaxValueValidator(100)],verbose_name="نسبة الاستشاري (%)")
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"),validators=[MinValueValidator(0), MaxValueValidator(100)],verbose_name="نسبة الإنجاز (%)")
    # Financing split (inputs)
    bank_finance_value  = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"),validators=[MinValueValidator(0)], verbose_name="إجمالي تمويل البنك")
    owner_finance_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"),validators=[MinValueValidator(0)], verbose_name="إجمالي تمويل المالك")
    # ================== Materialized totals (stored) ==================
    # Contract-level
    consultant_fees_value       = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # رسوم الاستشاري على العقد
    total_with_consultant       = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # العقد + الاستشاري

    # Variations aggregation
    variations_sum              = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # صافي أوامر التغيير
    variations_consultant_fees  = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # رسوم الاستشاري على الإضافات

    # Contract + Variations
    contract_plus_variations    = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    # To-Date (by completion %)
    payable_to_date             = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # (عقد+إضافات) × إنجاز
    consultant_to_date          = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # رسوم الاستشاري حتى تاريخه
    total_to_date               = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # مستحق + استشاري
    vat_to_date                 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # VAT 5%
    grand_total_to_date         = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # شامل الضريبة

    # Payments
    payments_sum                = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    remaining_to_pay            = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    # --------- helpers ----------
    def _q(self, x):  # quantize
        return Decimal(x or 0).quantize(TWOPL, rounding=ROUND_HALF_UP)

    def recalc_dates(self):
        # final_duration_months + end_date_with_extension
        dur = self.duration_months or 0
        ext_d = self.time_extension_days or 0
        self.final_duration_months = dur + ceil(ext_d / 30) if (dur or ext_d) else dur
        if self.start_date:
            base_end = self.start_date + relativedelta(months=dur)
            self.end_date_with_extension = base_end + timedelta(days=ext_d)
        else:
            self.end_date_with_extension = None

    def recalc_totals(self):
        """
        يعيد حساب كل المجاميع المخزنة اعتمادًا على المدخلات + الجداول الفرعية (VO/Payments)
        """
        cv   = self._q(self.contract_value)
        cpct = Decimal(self.consultant_percentage or 0) / Decimal("100")
        prog = Decimal(self.completion_percentage or 0) / Decimal("100")

        # رسوم الاستشاري على العقد
        consult_on_contract = self._q(cv * cpct)
        self.consultant_fees_value = consult_on_contract
        self.total_with_consultant = self._q(cv + consult_on_contract)

        # تجميع الإضافات
        vsum = Decimal("0.00")
        vfees = Decimal("0.00")
        for v in self.variation_orders.all():
            if getattr(v, "is_approved", True) is False:
                continue
            eff_pct = Decimal(v.effective_consultant_percentage or 0) / Decimal("100")
            vsum += (v.amount or 0)
            vfees += (v.amount or 0) * eff_pct
        self.variations_sum = self._q(vsum)
        self.variations_consultant_fees = self._q(vfees)

        # عقد + إضافات
        c_plus_v = cv + self.variations_sum
        self.contract_plus_variations = self._q(c_plus_v)

        # حتى تاريخه
        payable = self._q(c_plus_v * prog)
        consult_to_date = self._q((consult_on_contract + self.variations_consultant_fees) * prog)
        total_to_date = self._q(payable + consult_to_date)
        vat = self._q(total_to_date * VAT_RATE)
        grand = self._q(total_to_date + vat)

        self.payable_to_date     = payable
        self.consultant_to_date  = consult_to_date
        self.total_to_date       = total_to_date
        self.vat_to_date         = vat
        self.grand_total_to_date = grand

        # المدفوعات والمتبقي
        pay_sum = Decimal("0.00")
        for p in self.payments.all():
            pay_sum += (p.amount or 0)
        self.payments_sum = self._q(pay_sum)
        self.remaining_to_pay = self._q(grand - self.payments_sum)

    def save(self, *args, **kwargs):
        # تأكد من مزامنة تواريخ النهاية/المدة
        self.recalc_dates()
        # لاحقًا signals هتنادي recalc_totals؛ لكن عند الإنشاء/التعديل الأساسي نناديها هنا برضه
        super().save(*args, **kwargs)
        # بعد ما يبقى له pk نقدر نجمع من الأولاد
        self.recalc_totals()
        super().save(update_fields=[
            "consultant_fees_value", "total_with_consultant",
            "variations_sum", "variations_consultant_fees",
            "contract_plus_variations",
            "payable_to_date", "consultant_to_date", "total_to_date",
            "vat_to_date", "grand_total_to_date",
            "payments_sum", "remaining_to_pay",
            "final_duration_months", "end_date_with_extension",
        ])

    def __str__(self):
        return f"{self.project_code} - {self.project_number_fab}"

    class Meta:
        ordering = ["-project_number_fab"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class VariationOrder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="variation_orders")
    variation_number = models.CharField(max_length=100, verbose_name="رقم أمر التغيير")
    date = models.DateField(blank=True, null=True, verbose_name="تاريخ الاعتماد")
    # قد تكون سالبة (خصم)
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="قيمة أمر التغيير",
                                 validators=[MinValueValidator(Decimal("-9999999999.99"))])
    consultant_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة الاستشاري الخاصة بالأمر (%)"
    )
    is_approved = models.BooleanField(default=True, verbose_name="معتمد؟")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        ordering = ["date", "id"]
        unique_together = [("project", "variation_number")]
        verbose_name = "أمر تغيير"
        verbose_name_plural = "أوامر التغيير"

    @property
    def effective_consultant_percentage(self):
        """
        لو النسبة على مستوى الـ VO موجودة نستخدمها، وإلا نرجع نسبة المشروع.
        """
        if self.consultant_fee_percentage is not None:
            return self.consultant_fee_percentage
        return self.project.consultant_percentage or Decimal("0.00")

    @property
    def consultant_fee_amount(self):
        pct = Decimal(self.effective_consultant_percentage or 0) / Decimal("100")
        val = Decimal(self.amount or 0) * pct
        return val.quantize(TWOPL, rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.project.project_code} - {self.variation_number}"


class Payment(models.Model):
    class Source(models.TextChoices):
        CLIENT = "CLIENT", "Client Payment"
        BANK   = "BANK",   "Bank Payment"
        OTHER  = "OTHER",  "Other"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField(verbose_name="تاريخ")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="المبلغ")
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.CLIENT, verbose_name="الجهة/المصدر")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="وصف")

    class Meta:
        ordering = ["date", "id"]
        verbose_name = "دفعة"
        verbose_name_plural = "دفعات"

    def __str__(self):
        return f"{self.project.project_code} - {self.get_source_display()} - {self.amount}"
