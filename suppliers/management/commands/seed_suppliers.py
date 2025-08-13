import random
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from faker import Faker
from suppliers.models import Supplier, ScopeOfWork, SupplierGroup
from shared.models import Country, City, Bank
from django.contrib.auth import get_user_model

fake = Faker()

class Command(BaseCommand):
    help = "Seed 10 suppliers with sample data"

    def handle(self, *args, **kwargs):
        user = get_user_model().objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("❌ No users found. Create a user first."))
            return

        country = Country.objects.first()
        city = City.objects.filter(country=country).first()
        bank = Bank.objects.first()
        scope = ScopeOfWork.objects.first()
        group = SupplierGroup.objects.filter(scope_of_work=scope).first()

        if not all([country, city, bank, scope, group]):
            self.stdout.write(self.style.ERROR("❌ Missing required data in Country, City, Bank, ScopeOfWork, or SupplierGroup"))
            return

        for i in range(10):
            name_en = fake.company()
            name_ar = f"شركة {fake.first_name()} للتجارة"

            supplier = Supplier.objects.create(
                name_en=name_en,
                name_ar=name_ar,
                email=fake.company_email(),
                telephone_number=fake.phone_number(),
                whatsapp_number=fake.phone_number(),
                country=country,
                city=city,
                area=None,
                scope_of_work=scope,
                trn_number=fake.bothify(text='TRN#######'),
                supplier_history=random.choice(['new', 'previous']),
                supplier_type=random.choice(['supplier', 'subcontract']),
                branch_address=random.choice([
                    'Abu Dhabi', 'Dubai', 'Sharjah', 'Ajman', 'Umm Al Quwain', 'Fujairah', 'Ras Al Khaimah'
                ]),
                company_website=fake.url(),
                company_mailing_address=fake.address(),
                company_store_location=fake.url(),
                company_pickup_location=fake.url(),
                legal_structure=random.choice(['sole_proprietorship', 'partnership', 'llc']),
                bank=bank,
                account_holder_name=name_en,
                account_number=fake.bban(),
                iban_number=fake.iban(),
                created_by=user,
                updated_by=user,
            )

            supplier.supplier_group.set([group])
            # مرفقات وهمية
            supplier.trade_license_attachment.save("license.pdf", ContentFile(b"Dummy License"))
            supplier.iban_certificate.save("iban.pdf", ContentFile(b"Dummy IBAN"))
            supplier.ct_certificate.save("ct.pdf", ContentFile(b"Dummy CT"))
            supplier.authority_letter.save("auth.pdf", ContentFile(b"Dummy Letter"))
            supplier.poa.save("poa.pdf", ContentFile(b"Dummy POA"))

            self.stdout.write(self.style.SUCCESS(f"✅ Added supplier {supplier.name_en}"))

        self.stdout.write(self.style.SUCCESS("🎉 Done seeding 10 suppliers"))
