# customers/management/commands/seed_customers_random.py
import os
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.conf import settings

from faker import Faker

from customers.models import (
    Customer, Person, Company,
    AuthorizedPerson, ContactPerson, LegalPerson
)
from shared.models import (
    Country, City, Area, Gender, Nationality, Bank, Classification
)

fake = Faker()

# ===================== مسارات صور السيّد =====================
SEED_DIR = os.path.join(settings.BASE_DIR, "seed_images")
COMPANY_LOGO_PATH = os.path.join(SEED_DIR, "company_logo.jpg")
FEMALE_PHOTO_PATH = os.path.join(SEED_DIR, "female.jpg")
MALE_PHOTO_PATH   = os.path.join(SEED_DIR, "male.jpg")


# ===================== Tiny in-memory files (PNG/PDF) =====================
def tiny_png_bytes():
    # 1x1 PNG (fallback)
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def tiny_pdf_bytes(text="Seed File"):
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


def read_binary_if_exists(path: str) -> bytes | None:
    try:
        if path and os.path.exists(path) and os.path.isfile(path):
            with open(path, "rb") as f:
                return f.read()
        print(f"[seed] ⚠️ image not found: {path}")
    except Exception as e:
        print(f"[seed] ⚠️ error reading {path}: {e}")
    return None


# ===================== Helpers =====================
def ensure_admin_user():
    User = get_user_model()
    user = User.objects.first()
    if not user:
        user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )
    return user


def normalize_phone(p):
    s = str(p or "").strip()
    return s.replace(" ", "").replace("-", "")


def normalize_iban(iban):
    return str(iban or "").replace(" ", "").upper()


def rand_future(days=365):
    return date.today() + timedelta(days=random.randint(30, days))


def rand_past(years=30):
    return date.today() - timedelta(days=random.randint(30, 365 * years))


def pick_status():
    return random.choice(["active", "inactive", "pending"])


def ensure_shared_seed():
    # Countries, Cities, Areas
    countries = {
        "UAE": ["Abu Dhabi", "Dubai", "Sharjah"],
        "KSA": ["Riyadh", "Jeddah", "Dammam"],
        "Egypt": ["Cairo", "Giza", "Alexandria"],
    }
    for c_name, cities in countries.items():
        c, _ = Country.objects.get_or_create(name_en=c_name, defaults={"name_ar": c_name})
        for city_name in cities:
            city, _ = City.objects.get_or_create(
                name_en=city_name,
                defaults={"name_ar": city_name, "country": c},
                country=c,
            )
            for idx in range(1, 3):
                Area.objects.get_or_create(
                    name_en=f"Area {idx} - {city_name}",
                    defaults={"name_ar": f"حي {idx} - {city_name}", "city": city},
                    city=city,
                )

    for g in ["Male", "Female"]:
        Gender.objects.get_or_create(name_en=g, defaults={"name_ar": g})

    for n in ["Emirati", "Saudi", "Egyptian", "Indian", "Pakistani"]:
        Nationality.objects.get_or_create(name_en=n, defaults={"name_ar": n})

    for b in ["ADCB", "ENBD", "FAB", "Dubai Islamic Bank", "Mashreq"]:
        Bank.objects.get_or_create(name_en=b, defaults={"name_ar": b, "code": f"B-{b[:3].upper()}"})

    Classification.objects.get_or_create(name_en="General", defaults={"name_ar": "عام"})


def pick_geo():
    country = Country.objects.order_by("?").first()
    if not country:
        ensure_shared_seed()
        country = Country.objects.order_by("?").first()
    city = City.objects.filter(country=country).order_by("?").first()
    area = Area.objects.filter(city=city).order_by("?").first() if city else None
    return country, city, area


def pick_gender_nat():
    gender = Gender.objects.order_by("?").first()
    nationality = Nationality.objects.order_by("?").first()
    return gender, nationality


def pick_bank():
    return Bank.objects.order_by("?").first() or Bank.objects.first()


# ===================== Photo assignment helpers =====================
def assign_personal_photo(obj, preferred: str | None = None):
    """
    يختار صورة الراجل/البنت تلقائيًا لكل كيان Person/AuthorizedPerson/LegalPerson.
    - preferred: "male" أو "female" (اختياري)
    """
    male_bytes = read_binary_if_exists(MALE_PHOTO_PATH)
    female_bytes = read_binary_if_exists(FEMALE_PHOTO_PATH)

    if preferred == "male" and male_bytes:
        save_filefield(obj.personal_image_attachment, "male.jpg", male_bytes)
        return
    if preferred == "female" and female_bytes:
        save_filefield(obj.personal_image_attachment, "female.jpg", female_bytes)
        return

    # اختيار عشوائي مع fallback
    if male_bytes and female_bytes:
        if random.choice([True, False]):
            save_filefield(obj.personal_image_attachment, "male.jpg", male_bytes)
        else:
            save_filefield(obj.personal_image_attachment, "female.jpg", female_bytes)
    elif male_bytes:
        save_filefield(obj.personal_image_attachment, "male.jpg", male_bytes)
    elif female_bytes:
        save_filefield(obj.personal_image_attachment, "female.jpg", female_bytes)
    else:
        save_filefield(obj.personal_image_attachment, "fallback.png", tiny_png_bytes())


def assign_company_logo(company_obj):
    """
    يضع لوجو الشركة فقط في Company.logo_attachment.
    """
    logo_bytes = read_binary_if_exists(COMPANY_LOGO_PATH)
    if logo_bytes:
        save_filefield(company_obj.logo_attachment, "company_logo.jpg", logo_bytes)
    else:
        save_filefield(company_obj.logo_attachment, "fallback_logo.png", tiny_png_bytes())


# ===================== Fillers for mixins =====================
def fill_contact_info(obj, country=None, city=None, area=None):
    obj.email = fake.email()
    obj.telephone_number = normalize_phone(fake.phone_number())
    obj.whatsapp_number = normalize_phone(fake.phone_number())
    obj.country = country
    obj.city = city
    obj.area = area


def fill_base_person(obj, gender=None, nationality=None, prefer_photo: str | None = None):
    obj.birth_date = rand_past(50)
    obj.home_address = fake.address().replace("\n", " ")
    obj.gender = gender
    obj.nationality = nationality

    obj.national_id_number = str(fake.random_number(digits=10))
    obj.national_id_expiry_date = rand_future()
    save_filefield(obj.national_id_attachment, "nid.pdf", tiny_pdf_bytes("National ID"))

    obj.passport_number = str(fake.random_number(digits=9))
    obj.passport_expiry_date = rand_future()
    save_filefield(obj.passport_attachment, "passport.pdf", tiny_pdf_bytes("Passport"))

    save_filefield(obj.signature_attachment, "signature.png", tiny_png_bytes())
    assign_personal_photo(obj, preferred=prefer_photo)  # ← صورة الراجل/البنت


def fill_base_company(obj):
    obj.trade_license_number = f"TL-{fake.random_number(digits=7)}"
    obj.trade_license_expiry_date = rand_future()
    save_filefield(obj.trade_license_attachment, "trade_license.pdf", tiny_pdf_bytes("Trade License"))

    save_filefield(obj.stamp_attachment, "company_stamp.png", tiny_png_bytes())
    assign_company_logo(obj)  # ← لوجو الشركة فقط

    obj.classification = Classification.objects.first()
    obj.postal_code = str(fake.postcode())
    obj.landline_number = normalize_phone(fake.phone_number())
    obj.office_address = fake.address().replace("\n", " ")
    obj.map_location = "https://maps.example.com/" + fake.slug()
    obj.establishment_date = rand_past(40)
    obj.company_fax = normalize_phone(fake.phone_number())


def fill_bank_info(customer):
    customer.bank = pick_bank()
    customer.account_holder_name = customer.name_en or customer.name_ar or "Account Holder"
    customer.account_number = str(fake.random_number(digits=10))
    customer.iban_number = normalize_iban(f"AE{fake.random_number(digits=20)}")
    save_filefield(customer.iban_certificate, "iban.pdf", tiny_pdf_bytes("IBAN Certificate"))


# ===================== Command =====================
class Command(BaseCommand):
    help = "Seed fully synthetic customers (owners/commercial/consultant) incl. images/files, using photos from seed_images."

    def add_arguments(self, parser):
        parser.add_argument("--owners", type=int, default=10, help="Number of owner customers")
        parser.add_argument("--commercial", type=int, default=8, help="Number of commercial customers")
        parser.add_argument("--consultants", type=int, default=6, help="Number of consultant customers")
        parser.add_argument("--contacts-per-company", type=int, default=2)
        parser.add_argument("--authorized-per-owner", type=int, default=2)
        parser.add_argument("--with-legal-person", action="store_true", help="Always create LegalPerson for company customers")

    @transaction.atomic
    def handle(self, *args, **options):
        # لوج تشخيصي بسيط
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        print(f"[seed] MEDIA_ROOT={settings.MEDIA_ROOT}")
        print(f"[seed] SEED_DIR={SEED_DIR}")
        print(f"[seed] exists logo={os.path.exists(COMPANY_LOGO_PATH)}, female={os.path.exists(FEMALE_PHOTO_PATH)}, male={os.path.exists(MALE_PHOTO_PATH)}")

        admin_user = ensure_admin_user()
        ensure_shared_seed()

        owners = options["owners"]
        commercials = options["commercial"]
        consultants = options["consultants"]
        contacts_per_company = options["contacts_per_company"]
        authorized_per_owner = options["authorized_per_owner"]
        force_legal = options["with_legal_person"]

        total_created = 0

        # ========= Owners =========
        for idx in range(owners):
            try:
                country, city, area = pick_geo()
                gender, nationality = pick_gender_nat()

                cust = Customer(
                    customer_type="owner",
                    name_en=fake.name(),
                    name_ar=fake.name(),
                    status=pick_status(),
                    notes="Seeded (owner)",
                    created_by=admin_user,
                    updated_by=admin_user,
                )
                fill_contact_info(cust, country, city, area)
                fill_bank_info(cust)
                cust.save()

                # Person (1-1) — تناوب male/female
                prefer = "male" if idx % 2 == 0 else "female"
                p = Person(customer=cust)
                fill_base_person(p, gender, nationality, prefer_photo=prefer)
                fill_contact_info(p, country, city, area)
                p.save()

                # Authorized Persons (owner فقط)
                for j in range(authorized_per_owner):
                    ap = AuthorizedPerson(customer=cust)
                    ap.name_en = fake.name()
                    ap.name_ar = ap.name_en
                    ap_prefer = "female" if (idx + j) % 2 == 0 else "male"
                    fill_base_person(ap, gender, nationality, prefer_photo=ap_prefer)
                    fill_contact_info(ap, country, city, area)
                    save_filefield(ap.power_of_attorney_attachment, "poa_owner.pdf", tiny_pdf_bytes("POA Owner"))
                    ap.power_of_attorney_expiry_date = rand_future()
                    ap.save()

                total_created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Owner → {cust.code}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Owner row failed: {e}"))

        # ========= Company-like (commercial / consultant) =========
        def seed_company_like(kind, count):
            nonlocal total_created
            for k in range(count):
                try:
                    country, city, area = pick_geo()
                    gender, nationality = pick_gender_nat()

                    cust = Customer(
                        customer_type=kind,
                        name_en=fake.company(),
                        name_ar=fake.company(),
                        status=pick_status(),
                        notes=f"Seeded ({kind})",
                        created_by=admin_user,
                        updated_by=admin_user,
                    )
                    fill_contact_info(cust, country, city, area)
                    fill_bank_info(cust)
                    cust.save()

                    # Company (1-1)
                    comp = Company(customer=cust)
                    fill_base_company(comp)
                    comp.save()

                    # LegalPerson (اختياري)
                    if force_legal or random.choice([True, False]):
                        lp = LegalPerson(customer=cust)
                        lp.name_en = fake.name()
                        lp.name_ar = lp.name_en
                        lp_prefer = "female" if k % 2 == 0 else "male"
                        fill_base_person(lp, gender, nationality, prefer_photo=lp_prefer)
                        fill_contact_info(lp, country, city, area)
                        save_filefield(lp.power_of_attorney_attachment, "poa_company.pdf", tiny_pdf_bytes("Company POA"))
                        lp.power_of_attorney_expiry_date = rand_future()
                        lp.save()

                    # Contact people
                    for idx in range(contacts_per_company):
                        cp = ContactPerson(customer=cust)
                        cp.name_en = fake.name()
                        cp.name_ar = cp.name_en
                        fill_contact_info(cp, country, city, area)
                        cp.job_title = random.choice(["Manager", "Accountant", "HR", "Sales", "Procurement"])
                        cp.is_primary = (idx == 0)
                        cp.save()

                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ {kind.capitalize()} → {cust.code}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ {kind} row failed: {e}"))

        seed_company_like("commercial", commercials)
        seed_company_like("consultant", consultants)

        self.stdout.write(self.style.SUCCESS(f"🎯 Done. Created = {total_created}"))
