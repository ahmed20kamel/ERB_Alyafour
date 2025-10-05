from __future__ import annotations
from django.contrib import admin, messages
from django import forms
from django.utils.html import format_html
from django.utils.text import slugify
from django.urls import reverse
from django.db import transaction

from .models import (
    # القوالب (Proxy على FormTemplate)
    PreTenderTemplate, TemplateSection, SectionKind,
    # الأسئلة
    Question, QuestionOption,
    # التندر والإجابات والمرفقات (Proxies)
    PreTenderSubmission, AnswerBasic, Attachment,
    # عدّاد الأكواد (هنخفيه من القائمة)
    TenderCounter,
)

# ================ Helpers ================
def admin_link(label: str, url_name: str, params: dict | None = None):
    from urllib.parse import urlencode
    url = reverse(f"admin:{url_name}")
    if params:
        url = f"{url}?{urlencode(params)}"
    return format_html('<a href="{}">{}</a>', url, label)

# ================ Forms ================
class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        section = cleaned.get("section")
        if section and section.kind != SectionKind.BASIC:
            raise forms.ValidationError("الأسئلة لازم تكون داخل Section نوعه BASIC.")
        if not cleaned.get("q_key"):
            cleaned["q_key"] = slugify(cleaned.get("title") or "q")
        return cleaned

class TemplateSectionAdminForm(forms.ModelForm):
    """نقيّد الأدمن يختار BASIC فقط علشان البساطة."""
    class Meta:
        model = TemplateSection
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kind"].choices = [(SectionKind.BASIC, "Basic")]

# ================ Inlines ================
class TemplateSectionInline(admin.TabularInline):
    model = TemplateSection
    form = TemplateSectionAdminForm
    extra = 1
    fields = ("title", "section_key", "order")
    prepopulated_fields = {"section_key": ("title",)}
    show_change_link = True
    ordering = ("order", "id")

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0
    fields = ("value", "label", "order")
    ordering = ("order", "id")

class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionAdminForm
    extra = 0
    fields = ("q_key", "title", "q_type", "required", "order")
    show_change_link = True
    ordering = ("order", "id")

# ================ Templates ================
@admin.register(PreTenderTemplate)
class PreTenderTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "is_published", "created_by", "created_at", "sections_count", "open_sections")
    list_filter = ("is_published",)
    search_fields = ("title",)
    inlines = (TemplateSectionInline,)
    actions = ("duplicate_as_new_version", "publish_selected", "unpublish_selected")

    def sections_count(self, obj):
        return obj.sections.count()
    sections_count.short_description = "Sections"

    def open_sections(self, obj):
        return admin_link("Open sections", "pre_tender_templatesection_changelist", {"template__id__exact": obj.id})
    open_sections.short_description = "Manage"

    @admin.action(description="Duplicate as NEW version (unpublished)")
    def duplicate_as_new_version(self, request, queryset):
        created = 0
        for tpl in queryset:
            with transaction.atomic():
                new_tpl = PreTenderTemplate.objects.create(
                    title=tpl.title, version=tpl.version + 1, is_published=False, created_by=request.user
                )
                # انسخ السكاشن (BASIC فقط) + الأسئلة + الاختيارات
                sec_map = {}
                for sec in tpl.sections.filter(kind=SectionKind.BASIC).order_by("order", "id"):
                    sec_new = TemplateSection.objects.create(
                        template=new_tpl, kind=SectionKind.BASIC, section_key=sec.section_key,
                        title=sec.title, order=sec.order, ui=sec.ui
                    )
                    sec_map[sec.id] = sec_new

                for q in tpl.questions.filter(section__kind=SectionKind.BASIC).order_by("order", "id"):
                    q_new = Question.objects.create(
                        template=new_tpl, section=sec_map[q.section_id],
                        q_key=q.q_key, q_type=q.q_type, title=q.title,
                        description=q.description, required=q.required,
                        order=q.order, config=q.config, formula=q.formula
                    )
                    for opt in q.options.all().order_by("order", "id"):
                        QuestionOption.objects.create(
                            question=q_new, value=opt.value, label=opt.label, order=opt.order
                        )
                created += 1
        self.message_user(request, f"تم إنشاء {created} نسخة جديدة.", messages.SUCCESS)

    @admin.action(description="Publish selected")
    def publish_selected(self, request, queryset):
        n = queryset.update(is_published=True)
        self.message_user(request, f"تم نشر {n} قالب.", messages.SUCCESS)

    @admin.action(description="Unpublish selected")
    def unpublish_selected(self, request, queryset):
        n = queryset.update(is_published=False)
        self.message_user(request, f"تم إلغاء نشر {n} قالب.", messages.WARNING)

# ================ Sections ================
@admin.register(TemplateSection)
class TemplateSectionAdmin(admin.ModelAdmin):
    form = TemplateSectionAdminForm
    list_display = ("title", "template", "order")
    list_filter = ("template",)
    search_fields = ("title", "section_key")
    prepopulated_fields = {"section_key": ("title",)}
    ordering = ("order", "id")
    inlines = (QuestionInline,)

# ================ Questions ================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = ("title", "q_key", "q_type", "required", "template", "section", "order")
    list_filter = ("q_type", "required", "template", "section")
    search_fields = ("title", "q_key", "description")
    ordering = ("order", "id")
    inlines = (QuestionOptionInline,)
    prepopulated_fields = {"q_key": ("title",)}

@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "question", "order")
    list_filter = ("question__template",)
    search_fields = ("label", "value")
    ordering = ("order", "id")

# ================ Submissions ================
@admin.register(PreTenderSubmission)
class PreTenderSubmissionAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "status", "template", "created_by", "created_at", "rebuild_btn")
    list_filter = ("status", "template", "created_by")
    search_fields = ("code", "title")
    readonly_fields = ("schema_snapshot", "created_at", "code")
    actions = ("rebuild_snapshots",)

    fieldsets = (
        (None, {"fields": ("code", "title", "status", "template", "created_by", "created_at")}),
        ("Snapshot", {"fields": ("schema_snapshot",)}),
        ("Meta", {"fields": ("meta",)}),
    )

    def rebuild_btn(self, obj):
        return format_html('<span style="opacity:.8">استخدم الإجراء من الأعلى: "Rebuild snapshots"</span>')
    rebuild_btn.short_description = "Snapshot"

    @admin.action(description="Rebuild snapshots for selected DRAFT submissions")
    def rebuild_snapshots(self, request, queryset):
        count = 0
        for sub in queryset:
            if sub.status == "draft":
                sub.rebuild_snapshot()
                count += 1
        self.message_user(request, f"تم إعادة بناء Snapshot لـ {count} تندر.", messages.SUCCESS)

# نعرض الإجابات والمرفقات للقراءة فقط (Optional)
@admin.register(AnswerBasic)
class AnswerBasicAdmin(admin.ModelAdmin):
    list_display = ("tender", "question", "short_value")
    list_filter = ("tender__template", "question__section")
    search_fields = ("tender__code", "question__q_key", "question__title")
    readonly_fields = ("tender", "question", "value", "label_at_submit", "type_at_submit", "submitted_at")
    def short_value(self, obj): return str(obj.value)[:80]

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("tender", "type", "name", "uploaded_at")
    list_filter = ("tender__template", "type__section")
    search_fields = ("tender__code", "name", "type__name")
    readonly_fields = ("tender", "type", "file", "name", "uploaded_at")

# نخفي عدّاد الأكواد من القائمة (لكن نسيبه مسجّل لو احتجته)
@admin.register(TenderCounter)
class TenderCounterAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
    actions = []

# ==== نهاية النسخة الخفيفة ====
