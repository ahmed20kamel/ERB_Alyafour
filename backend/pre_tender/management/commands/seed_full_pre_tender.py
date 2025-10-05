# pre_tender/management/commands/seed_full_pre_tender.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from pre_tender.models import (
    FormTemplate, Section, Field, Option, Tender
)

User = get_user_model()


# ---------- helpers ----------
def add_select_options(field: Field, items):
    for i, it in enumerate(items, start=1):
        if isinstance(it, str):
            Option.objects.create(field=field, value=it, label=it, order=i)
        else:
            Option.objects.create(
                field=field,
                value=str(it.get("value") or it.get("id") or ""),
                label=str(it.get("label") or it.get("name") or it.get("value") or it.get("id") or ""),
                order=i,
            )


def mk_field(
    section: Section, *,
    key, label, ftype,
    order=1, required=False, enabled=True,
    ui=None, config=None, options=None
):
    f = Field.objects.create(
        section=section,
        key=key,
        label=label,
        type=ftype,
        required=required,
        enabled=enabled,
        order=order,
        ui=(ui or {}),
        config=(config or {}),
    )
    if ftype in ("select", "multiselect") and options:
        add_select_options(f, options)
    return f


class Command(BaseCommand):
    help = (
        "Seed a full Pre-Tender form template (sections, fields, options). "
        "Default: archive old templates and create a new ACTIVE one.\n"
        "Flags:\n"
        "  --reassign-drafts  Reassign all DRAFT tenders to the new template, then try deleting archived templates with no references.\n"
        "  --purge-all        DELETE all tenders & templates first (DANGEROUS)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--reassign-drafts", action="store_true", help="Reassign DRAFT tenders to the new template")
        parser.add_argument("--purge-all", action="store_true", help="Delete ALL tenders & templates before seeding (DANGEROUS)")

    @transaction.atomic
    def handle(self, *args, **opts):
        reassign_drafts = opts.get("reassign_drafts")
        purge_all = opts.get("purge_all")

        if purge_all:
            self.stdout.write(self.style.WARNING("PURGE MODE: deleting ALL tenders & templates…"))
            Tender.objects.all().delete()
            FormTemplate.objects.all().delete()

        # أرشفة أي قوالب موجودة
        existing_count = FormTemplate.objects.count()
        if existing_count:
            FormTemplate.objects.update(is_active=False)
            self.stdout.write(self.style.WARNING(f"Archived {existing_count} existing template(s)."))

        # إنشاء قالب نشط جديد
        tpl = FormTemplate.objects.create(title="Company Pre-Tender Form", is_active=True)
        self.stdout.write(self.style.SUCCESS(f"Created new ACTIVE template: {tpl.title}"))

        # =======================
        # 1) Project Details
        # =======================
        s_details = Section.objects.create(template=tpl, title="Project Details", order=10, ui={"cols": 3})
        mk_field(s_details, key="emirate", label="Emirate", ftype="select", order=10, required=True,
                 options=["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"])
        mk_field(s_details, key="area", label="Area", ftype="select", order=20, required=True,
                 options=["Downtown", "Marina", "JVC", "JLT", "Business Bay", "Other"])
        mk_field(s_details, key="sector_number", label="Sector Number", ftype="text", order=30)
        mk_field(s_details, key="plot_number", label="Plot Number", ftype="text", order=40)
        mk_field(s_details, key="project_name", label="Project Name", ftype="text", order=50, required=True, ui={"span": 2})
        mk_field(s_details, key="project_location_link", label="Project Location Link", ftype="text", order=60, ui={"span": 2})
        mk_field(s_details, key="project_number", label="Project Number", ftype="text", order=70)
        mk_field(s_details, key="project_id", label="Project ID", ftype="text", order=80)
        mk_field(s_details, key="dasd", label="DASD", ftype="text", order=90)
        mk_field(s_details, key="project_consultant", label="Project Consultant", ftype="select", order=100,
                 options=["AECOM", "KEO", "Parsons", "WSP", "Dar", "Other"])

        # =======================
        # 2) Pre-Tender Timeline
        # =======================
        s_time = Section.objects.create(template=tpl, title="Pre Tender Timeline", order=20, ui={"cols": 1})
        mk_field(s_time, key="pre_tender_deadline", label="Pre Tender Deadline", ftype="date", order=10, required=True)

        # =======================
        # 3) Project Areas (3 كروت)
        # =======================
        s_areas = Section.objects.create(
            template=tpl,
            title="Project Areas (Group)",
            order=30,
            ui={"cols": 3}
        )

        # جدول 1: Project Areas (Main) — بدون Sub Area (عشان الحقل الزايد)
        mk_field(
            s_areas,
            key="project_area_table",
            label="Project Areas",
            ftype="table",
            order=10,
            ui={"span": 1},
            config={
                "variant": "area",
                "columns": [
                    {"key": "main_area", "label": "Main Area", "type": "text"},
                    {"key": "units",     "label": "Units",     "type": "select", "options": ["SQ M", "L.M", "NOS"]},
                    {"key": "qty",       "label": "Quantity",  "type": "number"},
                ],
                "preset_rows": [
                    {"main_area": "Built-up Area"},
                    {"main_area": "External work"},
                    {"main_area": "Boundary Wall"},
                ],
                "lock_rows": True,      # يقفل الأعمدة اللي فيها قيم preset (Main Area)
                "show_total": True,
                "total_column": "qty",
            },
        )

        # جدول 2: Wet Area
        mk_field(
            s_areas,
            key="wet_area_table",
            label="Project Areas — WET AREA",
            ftype="table",
            order=20,
            ui={"span": 1},
            config={
                "variant": "area",
                "columns": [
                    {"key": "sub_area", "label": "Sub Area", "type": "text"},
                    {"key": "units",    "label": "Units",    "type": "select", "options": ["NOS", "SQ M", "L.M"]},
                    {"key": "qty",      "label": "Quantity", "type": "number"},
                ],
                "preset_rows": [
                    {"sub_area": "Toilet / Wash"},
                    {"sub_area": "Bathroom"},
                    {"sub_area": "Kitchen / Laundry / Pantry"},
                    {"sub_area": "BALCONY"},
                ],
                "lock_rows": True,
                "show_total": True,
                "total_column": "qty",
            },
        )

        # جدول 3: Dry Area
        mk_field(
            s_areas,
            key="dry_area_table",
            label="Project Areas — DRY AREA",
            ftype="table",
            order=30,
            ui={"span": 1},
            config={
                "variant": "area",
                "columns": [
                    {"key": "sub_area", "label": "Sub Area", "type": "text"},
                    {"key": "units",    "label": "Units",    "type": "select", "options": ["NOS", "SQ M", "L.M"]},
                    {"key": "qty",      "label": "Quantity", "type": "number"},
                ],
                "preset_rows": [
                    {"sub_area": "Majlis"},
                    {"sub_area": "Dinning"},
                    {"sub_area": "Bedroom"},
                    {"sub_area": "Living Room"},
                    {"sub_area": "Storage"},
                    {"sub_area": "LOBBY/HALL"},
                    {"sub_area": "Office"},
                    {"sub_area": "GYM"},
                ],
                "lock_rows": True,
                "show_total": True,
                "total_column": "qty",
            },
        )

        # =======================
        # 4) Project Components
        # =======================
        s_components = Section.objects.create(
            template=tpl, title="Project Components", order=40, ui={"variant": "checkboxes"}
        )
        mk_field(s_components, key="components_blocks", label="Project Components", ftype="multiselect", order=10,
                 options=["VILLA BLOCK", "SERVICE BLOCK", "ELEC ROOM", "Boundary Wall", "GARBAGE ROOM"])
        mk_field(s_components, key="villa_levels", label="VILLA BLOCK LEVELS", ftype="multiselect", order=20,
                 options=["BASEMENT", "GROUND FLOOR", "FIRST FLOOR", "ROOF FLOOR"])
        mk_field(s_components, key="foundation", label="Project Foundation", ftype="multiselect", order=30,
                 options=["Piling Foundation", "Isolated Foundation", "Strip Foundations"])
        mk_field(s_components, key="boundary_wall_finishing", label="Boundary Wall FINISHING", ftype="multiselect", order=40,
                 options=["PAINT", "STONE", "ALUMINUM CLADDING"])
        mk_field(s_components, key="interior_design", label="INTERIOR DESIGN", ftype="multiselect", order=50,
                 options=["YES", "NO"])
        mk_field(s_components, key="elevation_finishing", label="ELEVATION FINISHING", ftype="multiselect", order=60,
                 options=["PAINT", "STONE", "ALUMINUM CLADDING"])

        # =======================
        # 5) Funding Sources
        # =======================
        s_funding = Section.objects.create(
            template=tpl, title="Funding Sources", order=50, ui={"cols": 2}
        )
        mk_field(
            s_funding, key="bank_funding", label="Bank Funding (AED)",
            ftype="number", order=10, required=False, ui={"span": 1},
            config={"min": 0, "format": "currency"}
        )
        mk_field(
            s_funding, key="owner_funding", label="Owner Funding (AED)",
            ftype="number", order=20, required=False, ui={"span": 1},
            config={"min": 0, "format": "currency"}
        )

        # =======================
        # 6) Financial Summary
        # =======================
        s_fin = Section.objects.create(
            template=tpl,
            title="Financial Summary",
            order=60,
            ui={"cols": 2}
        )
        mk_field(
            s_fin, key="total_amount", label="Total Project Amount (AED)",
            ftype="number", order=10, required=True, ui={"span": 2},
            config={"min": 0}
        )
        mk_field(s_fin, key="basic_fee_enabled", label="Enable Basic Consultation Fees", ftype="checkbox", order=20)
        mk_field(s_fin, key="basic_fee_rate",    label="Basic Consultation Fee Rate (%)", ftype="number", order=30, config={"min": 0, "max": 100})
        mk_field(
            s_fin, key="basic_fee_amount", label="Fee Amount (AED)",
            ftype="number", order=40, config={"readonly": True, "min": 0}
        )
        mk_field(s_fin, key="addl_fee_enabled", label="Enable Additional Consultation Fees", ftype="checkbox", order=50)
        mk_field(s_fin, key="addl_fee_rate",    label="Additional Fee Rate (%)", ftype="number", order=60, config={"min": 0, "max": 100})
        mk_field(
            s_fin, key="addl_fee_amount", label="Fee Amount (AED)",
            ftype="number", order=70, config={"readonly": True, "min": 0}
        )

        # =======================
        # 7) Documents (attachments)
        # =======================
        s_docs = Section.objects.create(template=tpl, title="Documents", order=70, ui={"cols": 2})
        mk_field(
            s_docs, key="drawings", label="Drawings",
            ftype="file", order=10, required=True,
            config={"accept": [".pdf", ".dwg"], "hint": "PDF/DWG only"}
        )
        mk_field(
            s_docs, key="vendor_list", label="Vendor List",
            ftype="file", order=20, required=False,
            config={"accept": [".xlsx", ".csv", ".pdf"], "hint": "Excel/CSV/PDF"}
        )
        mk_field(
            s_docs, key="specifications", label="Specifications",
            ftype="file", order=30, required=False,
            config={"accept": [".pdf", ".doc", ".docx"], "hint": "PDF or Word"}
        )
        mk_field(
            s_docs, key="photos", label="Photos / Images",
            ftype="file", order=40, required=False,
            config={"accept": ["image/*"], "hint": "JPG/PNG"}
        )

        # =======================
        # 8) Pricing — Groups & Items (اختياري)
        # =======================
        PRICE_CARD_CONFIG = {
            "currency": "AED",
            "modes": {
                "LUMP_SUM": {"label": "Lump Sum", "show": ["final_price"]},
                "DETAILED": {"label": "Detailed", "show": ["rate", "unit", "notes"]},
            },
            "fields": {
                "final_price": {"label": "Final Price", "type": "number"},
                "rate": {"label": "Rate", "type": "number"},
                "unit": {"label": "Unit", "type": "select", "options": ["SQ M", "L.M", "NOS", "LS"]},
                "notes": {"label": "Technical Notes", "type": "textarea"},
            },
        }

        pricing_groups = [
            ("Finishes", [
                "Granite Floor", "Granite Tread and Riser", "Porcelain Floor", "Ceramic Floor",
                "Marble Floor", "Marble Tread and Riser", "Threshold", "Ceramic Skirting",
                "Marble Skirting", "Granite Skirting", "Ceramic Wall", "Aluminum False Ceiling",
                "Gypsum 60x60", "Gypsum Works and Decorations", "EXTERNAL ELEVATION FINISH",
            ]),
            ("MEP", ["Lighting", "Power", "Plumbing", "HVAC", "Fire Fighting", "Low Current"]),
            ("External Works", ["Boundary Wall", "Landscaping", "Interlock / Paving", "Parking", "Gates"]),
        ]

        base_order = 90
        for g_idx, (group_title, items) in enumerate(pricing_groups, start=1):
            sec = Section.objects.create(template=tpl, title=group_title, order=base_order + g_idx * 10, ui={"cols": 2})
            for i_idx, item in enumerate(items, start=1):
                mk_field(
                    sec,
                    key=f"price_{group_title.lower().replace(' ', '_').replace('/', '_')}_{i_idx}",
                    label=item,
                    ftype="price_card",
                    order=i_idx * 10,
                    ui={"span": 1},
                    config=PRICE_CARD_CONFIG,
                )

        # ---------- Reassign drafts & cleanup (optional) ----------
        if reassign_drafts:
            count = Tender.objects.filter(status="draft").update(template=tpl)
            self.stdout.write(self.style.WARNING(f"Reassigned {count} DRAFT tender(s) to the new template."))
            deleted, _ = FormTemplate.objects.filter(is_active=False).exclude(
                id__in=Tender.objects.values_list("template_id", flat=True).distinct()
            ).delete()
            if deleted:
                self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} archived template(s) not referenced by tenders."))

        self.stdout.write(self.style.SUCCESS("✔ Seed completed successfully."))
