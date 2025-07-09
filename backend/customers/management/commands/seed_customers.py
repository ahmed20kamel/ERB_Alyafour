import uuid
from faker import Faker
from django.core.management.base import BaseCommand
from customers.models import Customer, OwnerProfile, CompanyProfile, ContactPerson
from finance.models import Bank, BankAccount
from core.models import (
    Country, City, Nationality, Gender,
    Currency, CommunicationMethod, Billing, Classification
)


class Command(BaseCommand):
    help = "Seed the database with test customers and related data."

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting seeding process...")

        fake = Faker()

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

        bank, _ = Bank.objects.get_or_create(name="Seed Bank")

        counter = 1000
        for customer_type in customer_types:
            for i in range(1, 6):
                counter += 1
                suffix = uuid.uuid4().hex[:6].upper()

                # 👤 Create Customer
                customer = Customer.objects.create(
                    customer_type=customer_type,
                    full_name_arabic=f"{customer_type} عميل {i}",
                    full_name_english=f"{customer_type.capitalize()} Customer {i}",
                    email=f"{customer_type}{i}@example.com",
                    telephone_number=f"050{counter}",
                    whatsapp_number=f"051{counter}",
                    notes="Test seed customer",
                    status="active",
                    preferred_language="en",
                    birth_date="1990-01-01",
                    gender=choose(genders, i),
                    nationality=choose(nationalities, i),
                    national_id_number=f"NID{counter}{suffix}",
                    passport_number=f"PSP{counter}{suffix}",
                    national_id_expiry_date="2030-12-31",
                    passport_expiry_date="2030-12-31",
                    address=f"{customer_type.capitalize()} Address {i}",
                    phone_number=f"059{counter}",
                    country=choose(countries, i),
                    city=choose(cities, i),
                    currency=choose(currencies, i),
                    communication_method=choose(communications, i),
                    billing=choose(billings, i),
                )

                # 🏦 Add Bank Account
                BankAccount.objects.create(
                    bank=bank,
                    account_holder_name=customer.full_name_english,
                    account_number=f"ACC{counter}{suffix}",
                    iban_number=f"SA123456789{counter}",
                    iban_certificate_attachment="finance/iban_certificates/sample.pdf",
                    linked_customer=customer
                )

                # 👤 Owner Profile
                if customer_type == "owner":
                    OwnerProfile.objects.create(
                        customer=customer,
                        birth_date="1990-01-01",
                        address="Owner Address",
                        gender=choose(genders, i),
                        nationality=choose(nationalities, i),
                        national_id_number=f"OWNID{counter}{suffix}",
                        passport_number=f"OWNPASS{counter}{suffix}",
                        national_id_expiry_date="2030-12-31",
                        passport_expiry_date="2030-12-31",
                        national_id_attachment="owner/national_ids/sample.pdf",
                        passport_attachment="owner/passports/sample.pdf",
                        signature_attachment="owner/signatures/sample.png",
                        personal_image_attachment="owner/personal_images/sample.jpg",
                        authorized_person_name=f"Authorized Person {i}",
                        authorized_person_email=f"auth{i}@example.com",
                        authorized_person_phone_number=f"052{counter}",
                        authorized_person_birth_date="1985-05-05",
                        authorized_person_address="Authorized Address",
                        authorized_person_national_id_number=f"AUTHNID{counter}{suffix}",
                        authorized_person_national_id_attachment="authorized/national_ids/sample.pdf",
                        authorized_person_national_id_expiry_date="2030-01-01",
                        authorized_person_signature_attachment="authorized/signatures/sample.png",
                        authorized_person_personal_image_attachment="authorized/personal_images/sample.jpg",
                        authorized_person_passport_attachment="authorized/passports/sample.pdf",
                        authorized_person_passport_expiry_date="2030-01-01",
                        authorized_person_passport_number=f"AUTHPASS{counter}",
                        authorized_person_power_of_attorney_attachment="authorized/poa/sample.pdf",
                        authorized_person_power_of_attorney_expiry_date="2030-01-01"
                    )

                # 🏢 Company Profile + 4 ContactPerson
                if customer_type in ["consultant", "commercial"]:
                    company_profile = CompanyProfile.objects.create(
                        customer=customer,
                        classification=choose(classifications, i),
                        postal_code="12345",
                        landline_number=f"02{counter}",
                        company_office_address="Company HQ",
                        company_logo_attachment="company/logos/sample.png",
                        company_trade_license_attachment="company/licenses/sample.pdf",
                        company_trade_license_number=f"TL{counter}{suffix}",
                        company_trade_license_expiry_date="2030-12-31",
                        company_stamp_attachment="company/stamps/sample.png",
                        company_establishment_date="2010-01-01",
                        area="Business District",
                        map_location="https://maps.google.com/?q=24.7,46.7",
                        responsible_person_name=fake.name(),
                        responsible_person_birth_date="1980-01-01",
                        responsible_person_address="Home Address",

                        responsible_person_job_title="Manager",
                        responsible_person_email=f"resp{counter}@example.com",
                        responsible_person_phone_number=f"053{counter}",
                        responsible_person_national_id_number=f"RPNID{counter}{suffix}",
                        responsible_person_national_id_attachment="company/responsible_ids/sample.pdf",
                        responsible_person_national_id_expiry_date="2030-01-01",
                        responsible_person_signature_attachment="company/responsible_signatures/sample.png",
                        responsible_person_personal_image_attachment="company/responsible_images/sample.jpg",
                        responsible_person_passport_attachment="company/responsible_passports/sample.pdf",
                        responsible_person_passport_expiry_date="2030-01-01",
                        responsible_person_passport_number=f"RPPASS{counter}",
                        responsible_person_power_of_attorney_attachment="company/responsible_poa/sample.pdf",
                        responsible_person_power_of_attorney_expiry_date="2030-01-01",
                    )

                    for j in range(4):
                        ContactPerson.objects.create(
                            company_profile=company_profile,
                            name=f"Contact {j + 1} for {customer.full_name_english}",
                            job_title=fake.job(),
                            email=f"contact{j+1}@{customer_type}{i}.com",
                            phone_number=fake.phone_number(),
                            whatsapp_number=fake.phone_number(),
                            is_primary=(j == 0)
                        )

        self.stdout.write(self.style.SUCCESS("✅ All customers seeded successfully."))
