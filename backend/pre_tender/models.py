from __future__ import annotations
"""
Pre-Tender – Legacy-named Models with new capabilities
- يحافظ على أسماء الكلاسات القديمة (Tender/Answer/TenderFile/...)
- يضيف المعمارية الجديدة: Template + Sections ثابتة النوع + Areas/Components/Pricing/Funding/Fees/Attachments
- Snapshot لكل Tender + توليد كود متسلسل آمن + إجابات منفصلة حسب النوع
"""

from decimal import Decimal
from typing import Any

from django.db import models, transaction, IntegrityError
from django.db.models import F, Prefetch
from django.contrib.auth import get_user_model
# ======== Master Data (to satisfy admin.py imports) ========

class ProjectType(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Emirate(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class AreaLocation(models.Model):
    emirate = models.ForeignKey(Emirate, on_delete=models.CASCADE, related_name="areas")
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ("emirate", "name")
        ordering = ("emirate__name", "name")

    def __str__(self):
        return f"{self.emirate.name} / {self.name}"


class Consultant(models.Model):
    full_name_english = models.CharField(max_length=180)

    class Meta:
        ordering = ("full_name_english",)

    def __str__(self):
        return self.full_name_english

User = get_user_model()


# ===============================
# 1) Choices وأنواع ثابتة
# ===============================

class TenderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class SectionKind(models.TextChoices):
    BASIC = "basic", "Basic"
    AREAS_OVERALL = "project_areas_overall", "Project Areas – Overall"
    AREAS_GROUPED = "project_areas_grouped", "Project Areas – Grouped"
    COMPONENTS = "project_components", "Project Components"
    PRICING = "pricing", "Pricing"
    FUNDING = "funding_calc", "Funding & Calculations"
    FEES = "fees", "Consultation Fees"
    ATTACH = "attachments", "File Attachments"


class QuestionType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    SELECT = "select", "Select"
    MULTI_SELECT = "multi_select", "Multi Select"
    MONEY = "money", "Money"
    CALCULATION = "calculation", "Calculation"


class PricingMode(models.TextChoices):
    LUMP_SUM = "lump_sum", "Lump Sum"
    DETAILED = "detailed", "Detailed"


# ===============================
# 2) القالب والإصدارات
# ===============================

class FormTemplate(models.Model):
    """(كان: FormTemplate) — قالب بإصدارات ونشر."""
    title = models.CharField(max_length=200, default="Company Pre-Tender Form")
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=False)      # تقدر تسيبها قديمًا لو في كود بيعتمد عليها
    is_published = models.BooleanField(default=False)   # الجديد المعتمد
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("title", "version")
        ordering = ("-created_at", "-version", "title")
        verbose_name = "Form Template"
        verbose_name_plural = "Form Templates"

    def __str__(self):
        return f"{self.title} v{self.version}"


class TemplateSection(models.Model):
    """(كان: Section) — قسم ثابت النوع داخل القالب."""
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    section_key = models.SlugField(max_length=120, help_text="Stable key (e.g. basic_info)")
    kind = models.CharField(max_length=32, choices=SectionKind.choices)
    order = models.PositiveIntegerField(default=1)
    ui = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("template", "section_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.template} / {self.title}"


# =========================
# 3) Basic Questions
# =========================

class Question(models.Model):
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name="questions")
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="questions")
    q_key = models.SlugField(max_length=120, help_text="Stable key (e.g. project_name)")
    q_type = models.CharField(max_length=16, choices=QuestionType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    required = models.BooleanField(default=False)
    group_name = models.CharField(max_length=120, blank=True, default="")
    order = models.PositiveIntegerField(default=1)
    config = models.JSONField(default=dict, blank=True)
    formula = models.TextField(blank=True, null=True)  # لو CALCULATION

    class Meta:
        unique_together = ("template", "q_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.title} ({self.q_type})"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=160)
    label = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("question", "value")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.question.title}: {self.label}"


# ==================================
# 4) Project Areas – Overall/Grouped
# ==================================

class AreaOverallItem(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="area_overall_items")
    item_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    unit = models.CharField(max_length=32)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "item_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name} ({self.unit})"


class AreaGroup(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="area_groups")
    group_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    unit = models.CharField(max_length=32)  # وحدة ثابتة للمجموعة
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "group_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name} ({self.unit})"


class AreaGroupSubArea(models.Model):
    group = models.ForeignKey(AreaGroup, on_delete=models.CASCADE, related_name="subareas")
    sub_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("group", "sub_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.group.name} / {self.name}"


# ==================
# 5) Components
# ==================

class ComponentGroup(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="component_groups")
    group_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "group_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name}"


class ComponentOption(models.Model):
    group = models.ForeignKey(ComponentGroup, on_delete=models.CASCADE, related_name="options")
    opt_key = models.SlugField(max_length=120)
    label = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("group", "opt_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.group.name} / {self.label}"


# ==================
# 6) Pricing
# ==================

class PricingSection(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="pricing_sections")
    pr_section_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "pr_section_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name}"


class PricingItem(models.Model):
    pricing_section = models.ForeignKey(PricingSection, on_delete=models.CASCADE, related_name="items")
    item_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    default_unit = models.CharField(max_length=32, blank=True, default="")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("pricing_section", "item_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.pricing_section.name} / {self.name}"


# ==========================
# 7) Funding & Fees & Attachments
# ==========================

class FundingSource(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="funding_sources")
    source_key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "source_key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name}"


class FeeDefinition(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="fees")
    key = models.SlugField(max_length=60)
    name = models.CharField(max_length=120)
    default_rate = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0.000"))
    is_optional = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name} ({self.default_rate}%)"


class AttachmentType(models.Model):
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name="attachment_types")
    key = models.SlugField(max_length=60)
    name = models.CharField(max_length=120)
    accept = models.CharField(max_length=120, blank=True, default="")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "key")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.title} / {self.name}"


# ==========================
# 8) عدّاد الأكواد
# ==========================

class TenderCounter(models.Model):
    name = models.CharField(max_length=50, unique=True, default="default")
    value = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "pre_tender_tender_counter"

    @classmethod
    def next(cls) -> int:
        with transaction.atomic():
            row, _ = cls.objects.select_for_update().get_or_create(name="default", defaults={"value": 0})
            row.value = F("value") + 1
            row.save(update_fields=["value"])
            row.refresh_from_db(fields=["value"])
            return row.value


# ==========================
# 9) Tender (الاسم القديم)
# ==========================

class Tender(models.Model):
    """الاسم القديم مع القدرات الجديدة (Snapshot/Template/… الخ)."""
    code = models.CharField(max_length=12, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_tenders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=TenderStatus.choices, default=TenderStatus.DRAFT)

    template = models.ForeignKey(FormTemplate, on_delete=models.PROTECT, related_name="tenders")
    schema_snapshot = models.JSONField(default=dict, blank=True)  # الشكل النهائي المعروض
    meta = models.JSONField(default=dict, blank=True)

    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"[{self.code}] {self.title}"

    @staticmethod
    def _fmt_code(num: int) -> str:
        return str(num).zfill(3)

    @classmethod
    def create_with_snapshot(cls, *, user: User, title: str, meta: dict | None = None) -> "Tender":
        """ينشئ Tender بكود متسلسل + يلتقط Snapshot لأحدث قالب منشور."""
        with transaction.atomic():
            tpl = (FormTemplate.objects
                   .filter(is_published=True)
                   .order_by("-version", "-created_at")
                   .first())
            if not tpl:
                tpl = FormTemplate.objects.create(title="Default Pre-Tender Form", version=1, is_published=True, created_by=user)

        for _ in range(5):
            num = TenderCounter.next()
            code = cls._fmt_code(num)
            try:
                with transaction.atomic():
                    t = cls.objects.create(code=code, title=title, created_by=user, template=tpl, meta=(meta or {}))
                    t.rebuild_snapshot()
                    return t
            except IntegrityError:
                continue
        raise RuntimeError("Failed to allocate unique tender code after retries.")

    # -------- Snapshot مطابق للـ Front --------
    def rebuild_snapshot(self) -> None:
        if self.status != TenderStatus.DRAFT:
            return

        tpl = (FormTemplate.objects
               .filter(pk=self.template_id)
               .prefetch_related(
                   Prefetch("sections", queryset=TemplateSection.objects.order_by("order", "id").prefetch_related(
                       "area_overall_items",
                       Prefetch("area_groups", queryset=AreaGroup.objects.order_by("order", "id").prefetch_related(
                           Prefetch("subareas", queryset=AreaGroupSubArea.objects.order_by("order", "id"))
                       )),
                       Prefetch("component_groups", queryset=ComponentGroup.objects.order_by("order", "id").prefetch_related(
                           Prefetch("options", queryset=ComponentOption.objects.order_by("order", "id"))
                       )),
                       Prefetch("pricing_sections", queryset=PricingSection.objects.order_by("order", "id").prefetch_related(
                           Prefetch("items", queryset=PricingItem.objects.order_by("order", "id"))
                       )),
                       "funding_sources", "fees", "attachment_types", "questions",
                   )),
                   Prefetch("questions", queryset=Question.objects.order_by("order", "id").prefetch_related("options")),
               )
               .first())

        snap: dict[str, Any] = {"template": {"title": tpl.title, "version": tpl.version}, "sections": []}

        basic_by_section = {}
        for q in tpl.questions.all():
            basic_by_section.setdefault(q.section_id, []).append(q)

        for sec in tpl.sections.all():
            block: dict[str, Any] = {
                "id": sec.id, "kind": sec.kind, "key": sec.section_key,
                "title": sec.title, "order": sec.order, "ui": sec.ui or {},
            }

            if sec.kind == SectionKind.BASIC:
                block["fields"] = [{
                    "q_key": q.q_key,
                    "type": q.q_type,
                    "title": q.title,
                    "description": q.description,
                    "required": q.required,
                    "config": q.config,
                    "options": [{"value": o.value, "label": o.label} for o in q.options.all()],
                    "formula": q.formula,
                    "order": q.order,
                } for q in basic_by_section.get(sec.id, [])]

            elif sec.kind == SectionKind.AREAS_OVERALL:
                block["items"] = [{"key": it.item_key, "name": it.name, "unit": it.unit, "order": it.order}
                                  for it in sec.area_overall_items.all()]

            elif sec.kind == SectionKind.AREAS_GROUPED:
                block["groups"] = [{
                    "key": g.group_key, "name": g.name, "unit": g.unit, "order": g.order,
                    "subareas": [{"key": s.sub_key, "name": s.name, "order": s.order} for s in g.subareas.all()]
                } for g in sec.area_groups.all()]

            elif sec.kind == SectionKind.COMPONENTS:
                block["groups"] = [{
                    "key": g.group_key, "name": g.name, "order": g.order,
                    "options": [{"key": o.opt_key, "label": o.label, "order": o.order} for o in g.options.all()]
                } for g in sec.component_groups.all()]

            elif sec.kind == SectionKind.PRICING:
                block["work_types"] = [{
                    "key": ps.pr_section_key, "name": ps.name, "order": ps.order,
                    "sub_works": [{"key": it.item_key, "name": it.name, "unit": it.default_unit, "order": it.order}
                                  for it in ps.items.all()]
                } for ps in sec.pricing_sections.all()]

            elif sec.kind == SectionKind.FUNDING:
                block["sources"] = [{"key": fs.source_key, "name": fs.name, "order": fs.order}
                                    for fs in sec.funding_sources.all()]

            elif sec.kind == SectionKind.FEES:
                block["fees"] = [{"key": f.key, "name": f.name, "default_rate": float(f.default_rate),
                                  "is_optional": f.is_optional, "order": f.order}
                                 for f in sec.fees.all()]

            elif sec.kind == SectionKind.ATTACH:
                block["types"] = [{"key": at.key, "name": at.name, "order": at.order, "accept": at.accept}
                                  for at in sec.attachment_types.all()]

            snap["sections"].append(block)

        snap["sections"].sort(key=lambda s: (s.get("order", 9999), s["title"]))
        self.schema_snapshot = snap
        self.save(update_fields=["schema_snapshot"])


# ===================================
# 10) إجابات/قيم التندر
# ===================================

class Answer(models.Model):
    """
    توافقي:
    - الحقول القديمة: tender + field_key + value + label_at_submit + type_at_submit + submitted_at
    - دعم جديد (اختياري): question FK + computed
    """
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers")
    field_key = models.SlugField(max_length=120, db_index=True, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    value = models.JSONField(null=True, blank=True)
    computed = models.JSONField(null=True, blank=True)
    label_at_submit = models.CharField(max_length=200, blank=True, default="")
    type_at_submit = models.CharField(max_length=20, blank=True, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tender", "field_key")
        # ملحوظة: لو هتستخدم question فقط، سيب field_key فاضي؛ القيد ده هيشتغل لما يكون فيه field_key.


class AnswerAreaOverall(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers_area_overall")
    item = models.ForeignKey(AreaOverallItem, on_delete=models.PROTECT, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal("0.0000"))
    unit_snapshot = models.CharField(max_length=32)

    class Meta:
        unique_together = ("tender", "item")


class AnswerAreaGrouped(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers_area_grouped")
    subarea = models.ForeignKey(AreaGroupSubArea, on_delete=models.PROTECT, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal("0.0000"))
    unit_snapshot = models.CharField(max_length=32)

    class Meta:
        unique_together = ("tender", "subarea")


class AnswerComponent(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers_components")
    option = models.ForeignKey(ComponentOption, on_delete=models.PROTECT, related_name="+")
    checked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("tender", "option")


class AnswerPricing(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers_pricing")
    item = models.ForeignKey(PricingItem, on_delete=models.PROTECT, related_name="+")
    mode = models.CharField(max_length=12, choices=PricingMode.choices)
    amount_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)  # Lump Sum
    rate = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)          # Detailed
    unit = models.CharField(max_length=32, blank=True, default="")
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    technical_notes = models.TextField(blank=True, default="")
    line_total = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("tender", "item")

    def compute_line_total(self) -> Decimal:
        from decimal import ROUND_HALF_UP
        if self.mode == PricingMode.LUMP_SUM and self.amount_total is not None:
            return self.amount_total
        if self.mode == PricingMode.DETAILED and self.rate is not None and self.quantity is not None:
            return (self.rate * self.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")

    def save(self, *args, **kwargs):
        self.line_total = self.compute_line_total()
        super().save(*args, **kwargs)


class AnswerFunding(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers_funding")
    source = models.ForeignKey(FundingSource, on_delete=models.PROTECT, related_name="+")
    enabled = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    payment_details = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("tender", "source")


class AnswerFee(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="answers_fees")
    fee = models.ForeignKey(FeeDefinition, on_delete=models.PROTECT, related_name="+")
    enabled = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)   # %
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("tender", "fee")


# ==========================
# 11) مرفقات (الاسم القديم)
# ==========================

def tender_upload_path(instance: "TenderFile", filename: str) -> str:
    key = instance.field_key or (instance.type.key if instance.type_id else "file")
    return f"tenders/{instance.tender.code}/{key}/{filename}"


class TenderFile(models.Model):
    """
    الاسم القديم للمرفقات.
    حافظت على field_key القديم + ربط اختياري بـ AttachmentType الجديد.
    """
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="files")
    field_key = models.SlugField(max_length=120, blank=True, default="")
    type = models.ForeignKey(AttachmentType, on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    file = models.FileField(upload_to=tender_upload_path)
    name = models.CharField(max_length=255, blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tender.code} / {self.name or self.file.name}"


# ==========================
# 12) توافق اختياري (Overrides/CustomFields)
# ==========================
# عشان استيراد الأسماء القديمة ينجح حتى لو مش هتستخدمهم مع الـ Snapshot الجديد.

class TenderFieldOverride(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="field_overrides")
    field_key = models.SlugField(max_length=120)
    enabled = models.BooleanField(null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    required = models.BooleanField(null=True, blank=True)
    order = models.PositiveIntegerField(null=True, blank=True)
    config = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ("tender", "field_key")


class TenderCustomField(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="custom_fields")
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    section_title = models.CharField(max_length=200, null=True, blank=True)
    field_key = models.SlugField(max_length=120)
    label = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=QuestionType.choices)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=999)
    config = models.JSONField(default=dict, blank=True)
    options = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ("tender", "field_key")
        ordering = ["order", "id"]
# ==========================
# 13) Proxy models for legacy imports
# ==========================
# بتخلي الأسماء القديمة تشتغل بدون ما نكرر الجداول.

class PreTenderTemplate(FormTemplate):
    class Meta:
        proxy = True
        verbose_name = "PreTender Template (legacy)"
        verbose_name_plural = "PreTender Templates (legacy)"


class PreTenderSubmission(Tender):
    class Meta:
        proxy = True
        verbose_name = "PreTender Submission (legacy)"
        verbose_name_plural = "PreTender Submissions (legacy)"


class AnswerBasic(Answer):
    class Meta:
        proxy = True
        verbose_name = "Answer (basic, legacy)"
        verbose_name_plural = "Answers (basic, legacy)"


class Attachment(TenderFile):
    class Meta:
        proxy = True
        verbose_name = "Attachment (legacy)"
        verbose_name_plural = "Attachments (legacy)"
