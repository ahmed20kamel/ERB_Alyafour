# backend/customers/management/commands/seed_all.py
import os
import random
import shutil
from pathlib import Path
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from faker import Faker

from customers.models import (
    Customer, Person, Company,
    AuthorizedPerson, ContactPerson, LegalPerson
)
from shared.models import (
    Country, City, Area, Gender, Nationality, Bank, Classification
)

fake = Faker()

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

# ------------ Files (tiny PNG/PDF) ------------
def tiny_png_bytes():
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

# ------------ Helpers: normalize / trim ------------
def field_maxlen(obj, field_name: str, default: int | None = None) -> int | None:
    try:
        return getattr(obj._meta.get_field(field_name), "max_length", default) or default
    except Exception:
        return default

def trim_to_field(obj, field_name: str, value: str) -> str:
    if value is None:
        return value
    ml = field_maxlen(obj, field_name)
    s = str(value)
    return s[:ml] if ml else s

def normalize_phone(p: str) -> str:
    s = str(p or "").strip()
    return s.replace(" ", "").replace("-", "").replace("(", "").replace(")", "+")

def normalize_iban(iban: str) -> str:
    return str(iban or "").replace(" ", "").upper()

def rand_future(days=365):
    return date.today() + timedelta(days=random.randint(30, days))

def rand_past(years=30):
    return date.today() - timedelta(days=random.randint(30, 365 * years))

def pick_status():
    return random.choice(["active", "inactive", "pending"])

def ensure_admin_user(username="admin", email="admin@example.com", password="admin123"):
    User = get_user_model()
    user = User.objects.filter(username=username).first()
    if user:
        return user
    return User.objects.create_superuser(username=username, email=email, password=password)

# ------------ Seed images ------------
def read_binary_if_exists(path: Path) -> bytes | None:
    try:
        if path.exists() and path.is_file():
            return path.read_bytes()
    except Exception as e:
        print(f"[seed] ⚠️ error reading {path}: {e}")
    return None

def assign_personal_photo(obj, seed_dir: Path, preferred: str | None = None):
    male = read_binary_if_exists(seed_dir / "male.jpg")
    female = read_binary_if_exists(seed_dir / "female.jpg")
    if preferred == "male" and male:
        save_filefield(obj.personal_image_attachment, "male.jpg", male); return
    if preferred == "female" and female:
        save_filefield(obj.personal_image_attachment, "female.jpg", female); return
    if male and female:
        save_filefield(obj.personal_image_attachment,
                       "male.jpg" if random.choice([True, False]) else "female.jpg",
                       male if random.choice([True, False]) else female)
    elif male:
        save_filefield(obj.personal_image_attachment, "male.jpg", male)
    elif female:
        save_filefield(obj.personal_image_attachment, "female.jpg", female)
    else:
        save_filefield(obj.personal_image_attachment, "fallback.png", tiny_png_bytes())

def assign_company_logo(company_obj, seed_dir: Path):
    logo = read_binary_if_exists(seed_dir / "company_logo.jpg")
    if logo:
        save_filefield(company_obj.logo_attachment, "company_logo.jpg", logo)
    else:
        save_filefield(company_obj.logo_attachment, "fallback_logo.png", tiny_png_bytes())

# ------------ Fillers ------------
def fill_contact_info(obj, country=None, city=None, area=None):
    obj.email = trim_to_field(obj, "email", fake.email())
    obj.telephone_number = trim_to_field(obj, "telephone_number", normalize_phone(fake.phone_number()))
    obj.whatsapp_number  = trim_to_field(obj, "whatsapp_number",  normalize_phone(fake.phone_number()))
    obj.country = country
    obj.city = city
    obj.area = area

def fill_base_person(obj, seed_dir: Path, gender=None, nationality=None, prefer_photo: str | None = None):
    obj.birth_date = rand_past(50)
    obj.home_address = trim_to_field(obj, "home_address", fake.address().replace("\n", " "))
    obj.gender = gender
    obj.nationality = nationality

    obj.national_id_number = trim_to_field(obj, "national_id_number", str(fake.random_number(digits=10)))
    obj.national_id_expiry_date = rand_future()
    save_filefield(obj.national_id_attachment, "nid.pdf", tiny_pdf_bytes("National ID"))

    obj.passport_number = trim_to_field(obj, "passport_number", str(fake.random_number(digits=9)))
    obj.passport_expiry_date = rand_future()
    save_filefield(obj.passport_attachment, "passport.pdf", tiny_pdf_bytes("Passport"))

    save_filefield(obj.signature_attachment, "signature.png", tiny_png_bytes())
    assign_personal_photo(obj, seed_dir, preferred=prefer_photo)

def fill_base_company(obj, seed_dir: Path):
    obj.trade_license_number = trim_to_field(obj, "trade_license_number", f"TL-{fake.random_number(digits=7)}")
    obj.trade_license_expiry_date = rand_future()
    save_filefield(obj.trade_license_attachment, "trade_license.pdf", tiny_pdf_bytes("Trade License"))
    save_filefield(obj.stamp_attachment, "company_stamp.png", tiny_png_bytes())
    assign_company_logo(obj, seed_dir)

    obj.classification = Classification.objects.first()
    obj.postal_code = trim_to_field(obj, "postal_code", str(fake.postcode()))
    obj.landline_number = trim_to_field(obj, "landline_number", normalize_phone(fake.phone_number()))
    obj.office_address = trim_to_field(obj, "office_address", fake.address().replace("\n", " "))
    obj.map_location = trim_to_field(obj, "map_location", "https://maps.example.com/" + fake.slug())
    obj.establishment_date = rand_past(40)
    obj.company_fax = trim_to_field(obj, "company_fax", normalize_phone(fake.phone_number()))

def fill_bank_info(customer):
    iban_max = field_maxlen(customer, "iban_number", 34) or 34
    acc_max  = field_maxlen(customer, "account_number", 32) or 32
    holder_max = field_maxlen(customer, "account_holder_name", 128) or 128

    # بنك
    bank = Bank.objects.order_by("?").first()
    if not bank:
        bank = Bank.objects.create(name_en="Default Bank", name_ar="بنك افتراضي", code="BANK-DEF")
    customer.bank = bank

    holder = customer.name_en or customer.name_ar or "Account Holder"
    customer.account_holder_name = holder[:holder_max]

    acc = str(fake.random_number(digits=min(18, acc_max)))
    customer.account_number = trim_to_field(customer, "account_number", acc)

    iban = normalize_iban(f"AE{fake.random_number(digits=20)}")
    customer.iban_number = iban[:iban_max]

    save_filefield(customer.iban_certificate, "iban.pdf", tiny_pdf_bytes("IBAN Certificate"))

# ------------ Geo seeding (internal) ------------
def seed_geo_internal():
    # جنسيات/جندر/بنوك/تصنيفات
    for g in ["Male", "Female"]:
        Gender.objects.get_or_create(name_en=g, defaults={"name_ar": g})
    for n in ["Emirati", "Saudi", "Egyptian", "Indian", "Pakistani"]:
        Nationality.objects.get_or_create(name_en=n, defaults={"name_ar": n})
    for b in ["ADCB", "ENBD", "FAB", "Dubai Islamic Bank", "Mashreq"]:
        Bank.objects.get_or_create(name_en=b, defaults={"name_ar": b, "code": f"B-{b[:3].upper()}"})
    Classification.objects.get_or_create(name_en="General", defaults={"name_ar": "عام"})

    # Countries / Cities / Areas (3 دول × 3 مدن × 2 مناطق)
    data = {
        "UAE": ["Abu Dhabi", "Dubai", "Sharjah"],
        "KSA": ["Riyadh", "Jeddah", "Dammam"],
        "Egypt": ["Cairo", "Giza", "Alexandria"],
    }
    for c_name, cities in data.items():
        c, _ = Country.objects.get_or_create(name_en=c_name, defaults={"name_ar": c_name})
        for city_name in cities:
            city, _ = City.objects.get_or_create(
                name_en=city_name, defaults={"name_ar": city_name, "country": c}, country=c
            )
            for idx in range(1, 3):
                Area.objects.get_or_create(
                    name_en=f"Area {idx} - {city_name}",
                    defaults={"name_ar": f"حي {idx} - {city_name}", "city": city},
                    city=city,
                )

def pick_geo():
    country = Country.objects.order_by("?").first()
    city = City.objects.filter(country=country).order_by("?").first() if country else None
    area = Area.objects.filter(city=city).order_by("?").first() if city else None
    return country, city, area

def pick_gender_nat():
    gender = Gender.objects.order_by("?").first()
    nationality = Nationality.objects.order_by("?").first()
    return gender, nationality

# ------------ Command ------------
class Command(BaseCommand):
    help = "All-in-one seeder: (optional) reset → seed geo → seed customers with images → create admin"

    def add_arguments(self, parser):
        parser.add_argument("--reset-geo", action="store_true")
        parser.add_argument("--reset-customers", action="store_true")
        parser.add_argument("--flush-media", action="store_true")

        parser.add_argument("--owners", type=int, default=10)
        parser.add_argument("--commercial", type=int, default=8)
        parser.add_argument("--consultants", type=int, default=6)
        parser.add_argument("--contacts-per-company", type=int, default=2)
        parser.add_argument("--authorized-per-owner", type=int, default=2)
        parser.add_argument("--with-legal-person", action="store_true")

        parser.add_argument("--create-admin", action="store_true")
        parser.add_argument("--admin-user", type=str, default="admin")
        parser.add_argument("--admin-email", type=str, default="admin@example.com")
        parser.add_argument("--admin-password", type=str, default="admin123")

    def _flush_media_dirs(self):
        media = Path(settings.MEDIA_ROOT)
        if not media.exists():
            return
        for name in [
            "authorized", "company_logos", "company_stamps", "iban_certificates",
            "legal", "national_ids", "passports", "personal_images", "signatures",
            "trade_licenses", "uploads", "supplier_documents",
        ]:
            p = media / name
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)

    @transaction.atomic
    def handle(self, *args, **opt):
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        print(f"[seed_all] MEDIA_ROOT = {settings.MEDIA_ROOT}")

        # resets
        if opt["reset_customers"]:
            self.stdout.write(f"{YELLOW}🧹 Deleting customers & related...{END}")
            AuthorizedPerson.objects.all().delete()
            ContactPerson.objects.all().delete()
            LegalPerson.objects.all().delete()
            Person.objects.all().delete()
            Company.objects.all().delete()
            Customer.objects.all().delete()

        if opt["reset_geo"]:
            self.stdout.write(f"{YELLOW}🧹 Deleting geo (Country/City/Area)...{END}")
            Area.objects.all().delete()
            City.objects.all().delete()
            Country.objects.all().delete()

        if opt["flush_media"]:
            self.stdout.write(f"{YELLOW}🧹 Flushing MEDIA generated folders...{END}")
            self._flush_media_dirs()

        # seed geo (internal)
        self.stdout.write("🌍 Seeding GEO (internal)...")
        seed_geo_internal()

        # seed images dir info
        seed_dir = Path(settings.BASE_DIR) / "seed_images"
        print(f"[seed_all] SEED_DIR = {seed_dir}")
        print(f"[seed_all] exists male={ (seed_dir / 'male.jpg').exists() } "
              f"female={ (seed_dir / 'female.jpg').exists() } logo={ (seed_dir / 'company_logo.jpg').exists() }")

        # ensure admin (optional)
        if opt["create_admin"]:
            ensure_admin_user(opt["admin_user"], opt["admin_email"], opt["admin_password"])
            self.stdout.write(self.style.SUCCESS(f"✅ Admin ensured: {opt['admin_user']}"))

        owners = opt["owners"]
        commercials = opt["commercial"]
        consultants = opt["consultants"]
        contacts_per_company = opt["contacts_per_company"]
        authorized_per_owner = opt["authorized_per_owner"]
        force_legal = opt["with_legal_person"]

        total_created = 0

        # -------- Owners --------
        for idx in range(owners):
            try:
                country, city, area = pick_geo()
                gender, nationality = pick_gender_nat()

                cust = Customer(
                    customer_type="owner",
                    name_en=trim_to_field(Customer(), "name_en", fake.name()),
                    name_ar=trim_to_field(Customer(), "name_ar", fake.name()),
                    status=pick_status(),
                    notes=trim_to_field(Customer(), "notes", "Seeded (owner)"),
                )
                fill_contact_info(cust, country, city, area)
                fill_bank_info(cust)
                cust.save()

                prefer = "male" if idx % 2 == 0 else "female"
                p = Person(customer=cust)
                fill_base_person(p, seed_dir, gender, nationality, prefer_photo=prefer)
                fill_contact_info(p, country, city, area)
                p.save()

                for j in range(authorized_per_owner):
                    ap = AuthorizedPerson(customer=cust)
                    ap.name_en = trim_to_field(ap, "name_en", fake.name())
                    ap.name_ar = trim_to_field(ap, "name_ar", ap.name_en)
                    ap_prefer = "female" if (idx + j) % 2 == 0 else "male"
                    fill_base_person(ap, seed_dir, gender, nationality, prefer_photo=ap_prefer)
                    fill_contact_info(ap, country, city, area)
                    save_filefield(ap.power_of_attorney_attachment, "poa_owner.pdf", tiny_pdf_bytes("POA Owner"))
                    ap.power_of_attorney_expiry_date = rand_future()
                    ap.save()

                total_created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Owner → {cust.id}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Owner row failed: {e}"))

        # -------- Companies (commercial / consultant) --------
        def seed_company_like(kind, count):
            nonlocal total_created
            for k in range(count):
                try:
                    country, city, area = pick_geo()
                    gender, nationality = pick_gender_nat()

                    cust = Customer(
                        customer_type=kind,
                        name_en=trim_to_field(Customer(), "name_en", fake.company()),
                        name_ar=trim_to_field(Customer(), "name_ar", fake.company()),
                        status=pick_status(),
                        notes=trim_to_field(Customer(), "notes", f"Seeded ({kind})"),
                    )
                    fill_contact_info(cust, country, city, area)
                    fill_bank_info(cust)
                    cust.save()

                    comp = Company(customer=cust)
                    fill_base_company(comp, seed_dir)
                    comp.save()

                    if force_legal or random.choice([True, False]):
                        lp = LegalPerson(customer=cust)
                        lp.name_en = trim_to_field(lp, "name_en", fake.name())
                        lp.name_ar = trim_to_field(lp, "name_ar", lp.name_en)
                        lp_prefer = "female" if k % 2 == 0 else "male"
                        fill_base_person(lp, seed_dir, gender, nationality, prefer_photo=lp_prefer)
                        fill_contact_info(lp, country, city, area)
                        save_filefield(lp.power_of_attorney_attachment, "poa_company.pdf", tiny_pdf_bytes("Company POA"))
                        lp.power_of_attorney_expiry_date = rand_future()
                        lp.save()

                    for idx2 in range(contacts_per_company):
                        cp = ContactPerson(customer=cust)
                        cp.name_en = trim_to_field(cp, "name_en", fake.name())
                        cp.name_ar = trim_to_field(cp, "name_ar", cp.name_en)
                        fill_contact_info(cp, country, city, area)
                        cp.job_title = trim_to_field(cp, "job_title", random.choice(["Manager", "Accountant", "HR", "Sales", "Procurement"]))
                        cp.is_primary = (idx2 == 0)
                        cp.save()

                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ {kind.capitalize()} → {cust.id}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ {kind} row failed: {e}"))

        seed_company_like("commercial", commercials)
        seed_company_like("consultant", consultants)

        self.stdout.write(self.style.SUCCESS(f"🎯 Done. Created = {total_created}"))
