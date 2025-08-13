import os
import io
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
import pandas as pd
from faker import Faker

from customers.models import (
    Customer, Person, Company,
    AuthorizedPerson, ContactPerson, LegalPerson
)
from shared.models import (
    Country, City, Area, Gender, Nationality, Bank, Classification
)

fake = Faker()


# ===================== Helpers: in-memory files (PNG/PDF) =====================
def tiny_png_bytes():
    # 1x1 PNG (transparent) — صالح لحقول ImageField
    # مصدر: بايتات PNG قياسية لبيكسل واحد
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def tiny_pdf_bytes(text="Sample IBAN Certificate"):
    # PDF بسيط جداً بصفحة واحدة
    content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 56>>stream
BT /F1 12 Tf 10 180 Td ({text}) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/Name/F1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000102 00000 n
0000000285 00000 n
0000000412 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
531
%%EOF
"""
    return content.encode("latin-1")


def save_filefield(fieldfile, filename, data_bytes):
    fieldfile.save(filename, ContentFile(data_bytes), save=False)


# ===================== Lookups & get_or_create =====================
def get_or_create_country_city_area(country_name, city_name=None, area_name=None):
    country, _ = Country.objects.get_or_create(name_en=country_name, defaults={"name_ar": country_name})
    city = None
    area = None
    if city_name:
        city, _ = City.objects.get_or_create(name_en=city_name, defaults={"name_ar": city_name, "country": country}, country=country)
    if area_name and city:
        area, _ = Area.objects.get_or_create(name_en=area_name, defaults={"name_ar": area_name, "city": city}, city=city)
    return country, city, area


def get_fk_by_name(model, value_en, field="name_en"):
    if not value_en:
        return None
    try:
        return model.objects.get(**{f"{field}__iexact": str(value_en).strip()})
    except model.DoesNotExist:
        # fallback to create
        obj = model.objects.create(**{
            "name_en": str(value_en).strip(),
            "name_ar": str(value_en).strip(),
        })
        return obj


# ===================== Row → Customer payload mapping =====================
def normalize_phone(p):
    if not p:
        return ""
    s = str(p).strip()
    return s.replace(" ", "").replace("-", "")


def normalize_iban(iban):
    if not iban:
        return ""
    return str(iban).replace(" ", "").upper()


def pick_status():
    return random.choice(["active", "inactive", "pending"])


def rand_date_in_future(days=365):
    return date.today() + timedelta(days=random.randint(30, days))


def rand_past_date(years=10):
    return date.today() - timedelta(days=random.randint(30, 365 * years))


def ensure_admin_user():
    User = get_user_model()
    user = User.objects.first()
    if not user:
        # لو مافيش يوزر، ننشئ أدمن افتراضي بسيط
        user = User.objects.create_superuser(username="admin", email="admin@example.com", password="admin123")
    return user


# ===================== Create person/company blocks =====================
def fill_base_person(obj, gender=None, nationality=None):
    obj.birth_date = rand_past_date(50)
    obj.home_address = fake.address()
    obj.gender = gender
    obj.nationality = nationality

    obj.national_id_number = str(fake.random_number(digits=10))
    obj.national_id_expiry_date = rand_date_in_future()
    save_filefield(obj.national_id_attachment, "nid.pdf", tiny_pdf_bytes("National ID"))

    obj.passport_number = str(fake.random_number(digits=9))
    obj.passport_expiry_date = rand_date_in_future()
    save_filefield(obj.passport_attachment, "passport.pdf", tiny_pdf_bytes("Passport"))

    save_filefield(obj.signature_attachment, "signature.png", tiny_png_bytes())
    save_filefield(obj.personal_image_attachment, "avatar.png", tiny_png_bytes())


def fill_base_company(obj):
    obj.trade_license_number = f"TL-{fake.random_number(digits=7)}"
    obj.trade_license_expiry_date = rand_date_in_future()
    save_filefield(obj.trade_license_attachment, "trade_license.pdf", tiny_pdf_bytes("Trade License"))

    save_filefield(obj.stamp_attachment, "company_stamp.png", tiny_png_bytes())
    save_filefield(obj.logo_attachment, "company_logo.png", tiny_png_bytes())

    # تصنيف اختياري
    cls = Classification.objects.first() or Classification.objects.create(name_en="General", name_ar="عام")
    obj.classification = cls

    obj.postal_code = str(fake.postcode())
    obj.landline_number = normalize_phone(fake.phone_number())
    obj.office_address = fake.address().replace("\n", " ")
    obj.map_location = "https://maps.example.com/" + fake.slug()
    obj.establishment_date = rand_past_date(30)
    obj.company_fax = normalize_phone(fake.phone_number())


def fill_contact_info(obj, country=None, city=None, area=None):
    obj.email = fake.email()
    obj.telephone_number = normalize_phone(fake.phone_number())
    obj.whatsapp_number = normalize_phone(fake.phone_number())
    obj.country = country
    obj.city = city
    obj.area = area


def fill_bank_info(customer, bank=None):
    bank = bank or (Bank.objects.first() or Bank.objects.create(name_en="Default Bank", name_ar="بنك افتراضي", code="BANK-DEF"))
    customer.bank = bank
    customer.account_holder_name = customer.name_en or customer.name_ar or "Account Holder"
    customer.account_number = str(fake.random_number(digits=10))
    customer.iban_number = normalize_iban(f"AE{fake.random_number(digits=20)}")
    save_filefield(customer.iban_certificate, "iban_certificate.pdf", tiny_pdf_bytes("IBAN Certificate"))


# ===================== Excel mapping (optional) =====================
def map_row(row):
    """يتوقع أعمدة مثل عينتك، ويتسامح مع الغياب."""
    return {
        "name_en": row.get("full_name_english") or fake.name(),
        "name_ar": row.get("full_name_arabic") or fake.name(),
        "code": row.get("customer_code") or "",
        "customer_type": (str(row.get("customer_type")).strip().lower() if row.get("customer_type") else "owner"),
        "email": row.get("email") or fake.email(),
        "telephone_number": normalize_phone(row.get("telephone_number") or fake.phone_number()),
        "whatsapp_number": normalize_phone(row.get("whatsapp_number") or fake.phone_number()),
        "country_name": row.get("country") or "UAE",
        "city_name": row.get("city") or "Abu Dhabi",
        "area_name": row.get("area") or None,
        "gender_name": row.get("gender") or "Male",
        "nationality_name": row.get("nationality") or "Emirati",
        "bank_name": row.get("bank") or None,
        "bank_account": str(row.get("bank_account") or ""),
        "iban_number": normalize_iban(row.get("iban_number") or ""),
    }


# ===================== Command =====================
class Command(BaseCommand):
    help = "Seed customers (from Excel if provided) covering ALL model fields + image/file attachments."

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default="customers.xlsx", help="Excel file path (optional).")
        parser.add_argument("--count", type=int, default=20, help="How many random customers if no Excel.")
        parser.add_argument("--authorized-per-owner", type=int, default=2)
        parser.add_argument("--authorized-per-company", type=int, default=2)
        parser.add_argument("--contacts-per-company", type=int, default=2)
        parser.add_argument("--with-legal-person", action="store_true", help="Force create LegalPerson for company customers.")

    @transaction.atomic
    def handle(self, *args, **options):
        # ========= Ensure admin user =========
        admin_user = ensure_admin_user()

        # ========= Try Excel =========
        rows = []
        file_path = options["file"]
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                for _, r in df.iterrows():
                    rows.append(map_row(r))
                self.stdout.write(self.style.SUCCESS(f"📄 Loaded {len(rows)} rows from {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Could not read Excel ({e}). Falling back to random data."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No Excel file found. Falling back to random data."))

        # ========= Random fallback =========
        if not rows:
            # نولّد داتا متنوعة
            for _ in range(options["count"]):
                ctype = random.choice(["owner", "commercial", "consultant"])
                country_name = random.choice(["UAE", "KSA", "Egypt"])
                city_name = random.choice(["Abu Dhabi", "Dubai", "Riyadh", "Jeddah", "Cairo"])
                rows.append({
                    "name_en": fake.name(),
                    "name_ar": fake.name(),
                    "code": "",
                    "customer_type": ctype,
                    "email": fake.email(),
                    "telephone_number": normalize_phone(fake.phone_number()),
                    "whatsapp_number": normalize_phone(fake.phone_number()),
                    "country_name": country_name,
                    "city_name": city_name,
                    "area_name": None,
                    "gender_name": random.choice(["Male", "Female"]),
                    "nationality_name": random.choice(["Emirati", "Saudi", "Egyptian"]),
                    "bank_name": None,
                    "bank_account": str(fake.random_number(digits=9)),
                    "iban_number": normalize_iban(f"AE{fake.random_number(digits=20)}"),
                })

        created_count = 0
        skipped = 0

        for i, data in enumerate(rows, start=1):
            try:
                # ====== Lookups ======
                gender = get_fk_by_name(Gender, data["gender_name"])
                nationality = get_fk_by_name(Nationality, data["nationality_name"])
                country, city, area = get_or_create_country_city_area(data["country_name"], data["city_name"], data["area_name"])

                bank = None
                if data.get("bank_name"):
                    bank = get_fk_by_name(Bank, data["bank_name"])
                else:
                    bank = Bank.objects.first() or Bank.objects.create(name_en="Default Bank", name_ar="بنك افتراضي", code="BANK-DEF")

                # ====== Skip if code exists ======
                if data["code"] and Customer.objects.filter(code=data["code"]).exists():
                    skipped += 1
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipping existing code: {data['code']}"))
                    continue

                # ====== Customer ======
                customer = Customer(
                    name_en=data["name_en"],
                    name_ar=data["name_ar"],
                    code=data["code"] or "",  # سيُولّد تلقائياً لو فاضي
                    customer_type=data["customer_type"],
                    email=data["email"],
                    telephone_number=data["telephone_number"],
                    whatsapp_number=data["whatsapp_number"],
                    country=country,
                    city=city,
                    area=area,
                    status=pick_status(),
                    notes="Seeded via seed_customers_full",
                    created_by=admin_user,
                    updated_by=admin_user,
                )
                # بنك + آيبان
                fill_bank_info(customer, bank=bank)
                # لو جاي من الإكسل فيها أرقام حساب/آيبان نحترمها
                if data.get("bank_account"):
                    customer.account_number = str(data["bank_account"])
                if data.get("iban_number"):
                    customer.iban_number = data["iban_number"]

                customer.save()

                # ====== Owner → Person ======
                if customer.customer_type == "owner":
                    person = Person(customer=customer)
                    fill_base_person(person, gender=gender, nationality=nationality)
                    fill_contact_info(person, country=country, city=city, area=area)
                    person.save()

                    # AuthorizedPeople للمالك
                    for _ in range(options["authorized_per_owner"]):
                        ap = AuthorizedPerson(customer=customer)
                        # BasePerson + ContactInfo + Power of Attorney
                        fill_base_person(ap, gender=gender, nationality=nationality)
                        fill_contact_info(ap, country=country, city=city, area=area)
                        save_filefield(ap.power_of_attorney_attachment, "poa_owner.pdf", tiny_pdf_bytes("Power of Attorney"))
                        ap.power_of_attorney_expiry_date = rand_date_in_future()
                        # NameCodeBase
                        ap.name_en = fake.name()
                        ap.name_ar = ap.name_en
                        ap.save()

                # ====== Commercial/Consultant → Company + LegalPerson + ContactPeople ======
                else:
                    company = Company(customer=customer)
                    fill_base_company(company)
                    company.save()

                    # Legal Person (one-to-one)
                    if options["with_legal_person"] or random.choice([True, False]):
                        lp = LegalPerson(customer=customer)
                        fill_base_person(lp, gender=gender, nationality=nationality)
                        fill_contact_info(lp, country=country, city=city, area=area)
                        save_filefield(lp.power_of_attorney_attachment, "poa_company.pdf", tiny_pdf_bytes("Company POA"))
                        lp.power_of_attorney_expiry_date = rand_date_in_future()
                        lp.name_en = fake.name()
                        lp.name_ar = lp.name_en
                        lp.save()

                    # Contact people (many)
                    for idx in range(options["contacts_per_company"]):
                        cp = ContactPerson(customer=customer)
                        fill_contact_info(cp, country=country, city=city, area=area)
                        cp.name_en = fake.name()
                        cp.name_ar = cp.name_en
                        cp.job_title = random.choice(["Manager", "Accountant", "HR", "Sales"])
                        cp.is_primary = (idx == 0)
                        cp.save()

                    # Authorized people (many) حتى للشركات
                    for _ in range(options["authorized_per_company"]):
                        ap = AuthorizedPerson(customer=customer)
                        fill_base_person(ap, gender=gender, nationality=nationality)
                        fill_contact_info(ap, country=country, city=city, area=area)
                        save_filefield(ap.power_of_attorney_attachment, "poa_company_holder.pdf", tiny_pdf_bytes("POA Holder"))
                        ap.power_of_attorney_expiry_date = rand_date_in_future()
                        ap.name_en = fake.name()
                        ap.name_ar = ap.name_en
                        ap.save()

                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ [{i}] Created {customer.customer_type} → {customer.code or customer.id} - {customer.name_en}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Row {i} failed: {e}"))
                # لو حابب تكمل على باقي الصفوف بدون رول‑باك، ما تعملش atomic شامل

        self.stdout.write(self.style.SUCCESS(f"🎯 Done. Created: {created_count}, Skipped (existing code): {skipped}"))
