import uuid
from django.core.management.base import BaseCommand
from customers.models import (
    Customer, OwnerProfile, CompanyProfile, ContactPerson
)
from core.models import (
    Country, City, Nationality, Gender,
    Currency, CommunicationMethod, Billing, Classification
)
from finance.models import Bank, BankAccount


class Command(BaseCommand):
    help = "Seed the database with full customer test data."

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Seeding customers with full test data...")

        customer_types = ["owner", "consultant", "commercial"]
        genders = list(Gender.objects.all())
        countries = list(Country.objects.all())
        cities = list(City.objects.all())
        nationalities = list(Nationality.objects.all())
        currencies = list(Currency.objects.all())
        communications = list(CommunicationMethod.objects.all())
        billings = list(Billing.objects.all())
        classifications = list(Classification.objects.all())

        def choose(items, i):
            return items[i % len(items)] if items else None

        def random_user_image(index):
            gender = "men" if index % 2 == 0 else "women"
            return f"https://randomuser.me/api/portraits/{gender}/{index % 100}.jpg"

        counter = 1000
        bank, _ = Bank.objects.get_or_create(name="Sample Bank")

        for customer_type in customer_types:
            for i in range(1, 6):
                counter += 1
                unique_suffix = uuid.uuid4().hex[:6].upper()

                # 👤 إنشاء العميل
                customer = Customer.objects.create(
                    customer_type=customer_type,
                    full_name_arabic=f"{customer_type} عميل {i}",
                    full_name_english=f"{customer_type.capitalize()} Customer {i}",
                    email=f"{customer_type}{i}@example.com",
                    telephone_number=f"050{counter}",
                    whatsapp_number=f"051{counter}",
                    notes="عميل تجريبي",
                    status="active",
                    preferred_language="en",
                    country=choose(countries, i),
                    city=choose(cities, i),
                    currency=choose(currencies, i),
                    communication_method=choose(communications, i),
                    billing=choose(billings, i),
                    birth_date="1990-01-01",
                    gender=choose(genders, i),
                    nationality=choose(nationalities, i),
                    national_id_number=f"NID{counter}{unique_suffix}",
                    passport_number=f"PSP{counter}{unique_suffix}",
                    national_id_expiry_date="2030-12-31",
                    passport_expiry_date="2030-12-31",
                    address=f"Main address {i}",
                    phone_number=f"059{counter + 10}"
                )

                # 🏦 ربط حساب بنكي بالعميل
                bank_account = BankAccount.objects.create(
                    bank=bank,
                    account_holder_name=f"Account Holder {i}",
                    account_number=f"ACC{counter}{unique_suffix}",
                    iban_number=f"SA03{counter}{uuid.uuid4().hex[:8].upper()}",
                    iban_certificate_attachment="finance/iban_certificates/dummy_iban.pdf",
                    linked_customer=customer
                )

                customer.bank_account = bank_account
                customer.save()  # عشان نحفظ الربط

                # 👤 ملف Owner
                if customer_type == "owner":
                    OwnerProfile.objects.create(
                        customer=customer,
                        birth_date="1990-01-01",
                        address="Owner Address",
                        gender=choose(genders, i),
                        nationality=choose(nationalities, i),
                        national_id_number=f"OWNNID{counter}{unique_suffix}",
                        passport_number=f"OWNPASS{counter}{unique_suffix}",
                        national_id_expiry_date="2030-12-31",
                        passport_expiry_date="2030-12-31",
                        signature_attachment="dummy_signature.png",
                        personal_image_attachment=random_user_image(i + 10),
                        national_id_attachment="dummy_nid.png",
                        passport_attachment="dummy_passport.png",
                        authorized_person_name=f"Authorized Person {i}",
                        authorized_person_email=f"auth{i}@mail.com",
                        authorized_person_phone_number=f"052{counter}",
                        authorized_person_birth_date="1990-02-02",
                        authorized_person_address="Authorized Address",
                        authorized_person_national_id_number=f"AUTHNID{counter}{unique_suffix}",
                        authorized_person_national_id_attachment="auth_id.pdf",
                        authorized_person_national_id_expiry_date="2030-01-01",
                        authorized_person_passport_number=f"AUTHPASS{counter}{unique_suffix}",
                        authorized_person_passport_attachment="auth_passport.pdf",
                        authorized_person_passport_expiry_date="2030-01-01",
                        authorized_person_power_of_attorney_attachment="poa.pdf",
                        authorized_person_power_of_attorney_expiry_date="2030-01-01",
                        authorized_person_signature_attachment="auth_sign.png",
                        authorized_person_personal_image_attachment=random_user_image(i + 20),
                    )

                # 🏢 ملف شركة واستدعاء أشخاص التواصل
                if customer_type in ["consultant", "commercial"]:
                    company_profile = CompanyProfile.objects.create(
                        customer=customer,
                        classification=choose(classifications, i),
                        postal_code="12345",
                        landline_number=f"02{counter}",
                        company_office_address="Company HQ",
                        company_logo_attachment=f"https://source.unsplash.com/300x300/?corporate,logo&sig={i}",
                        company_trade_license_number=f"TL{counter}{unique_suffix}",
                        company_trade_license_attachment="license.pdf",
                        company_trade_license_expiry_date="2030-12-31",
                        company_stamp_attachment="stamp.png",
                        company_establishment_date="2010-01-01",
                        map_location=f"https://maps.google.com/?q=24.7{i},46.7{i}",
                        area="Sample Area",
                        responsible_person_name="John Doe",
                        responsible_person_birth_date="1985-05-20",
                        responsible_person_address="Home 1",
                        responsible_person_job_title="Manager",
                        responsible_person_phone_number=f"053{counter}",
                        responsible_person_email=f"responsible{counter}@example.com",
                        responsible_person_national_id_number=f"RPNID{counter}{unique_suffix}",
                        responsible_person_national_id_attachment="rp_id.pdf",
                        responsible_person_national_id_expiry_date="2030-01-01",
                        responsible_person_passport_number=f"RPPASS{counter}{unique_suffix}",
                        responsible_person_passport_attachment="rp_passport.pdf",
                        responsible_person_passport_expiry_date="2030-01-01",
                        responsible_person_power_of_attorney_attachment="poa.pdf",
                        responsible_person_power_of_attorney_expiry_date="2030-01-01",
                        responsible_person_signature_attachment="rp_sign.png",
                        responsible_person_personal_image_attachment=random_user_image(i + 30),
                    )

                    for j in range(2):
                        ContactPerson.objects.create(
                            company_profile=company_profile,
                            name=f"Contact {j + 1}",
                            job_title="Sales",
                            email=f"contact{j + 1}@{customer_type}{i}.com",
                            phone_number=f"054{counter}{j}",
                            whatsapp_number=f"056{counter}{j}",
                            is_primary=(j == 0)
                        )

        self.stdout.write(self.style.SUCCESS("✅ Unique customers created successfully."))
