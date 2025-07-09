from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    Gender, Country, City, Nationality,
    Currency, CommunicationMethod, Billing, Classification
)
from finance.models import Bank, BankAccount
from customers.models import (
    Customer, OwnerProfile, CompanyProfile, ContactPerson
)

class Command(BaseCommand):
    help = "Fully seed the database with lookups + demo customers."

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting full database seed...")

        # ------------------------
        # seed lookup data
        # ------------------------
        self.stdout.write("✅ Seeding lookup data...")

        countries = ["Egypt", "UAE", "Saudi Arabia", "USA", "Germany"]
        cities = ["Cairo", "Dubai", "Riyadh", "New York", "Berlin"]
        nationalities = ["Egyptian", "Emirati", "Saudi", "American", "German"]
        genders = ["Male", "Female", "Other"]
        currencies = ["EGP", "AED", "SAR", "USD", "EUR"]
        communication_methods = ["Email", "Phone", "WhatsApp"]
        billings = ["Monthly", "Quarterly", "Yearly"]
        classifications = ["A", "B", "C"]

        country_objs = []
        for name in countries:
            country, _ = Country.objects.get_or_create(name=name)
            country_objs.append(country)

        for name in cities:
            city, created = City.objects.get_or_create(name=name, defaults={'country': country_objs[0]})
            if not city.country:
                city.country = country_objs[0]
                city.save()

        for name in nationalities:
            Nationality.objects.get_or_create(name=name)

        for name in genders:
            Gender.objects.get_or_create(name=name)

        for name in currencies:
            Currency.objects.get_or_create(name=name)

        for name in communication_methods:
            CommunicationMethod.objects.get_or_create(name=name)

        for name in billings:
            Billing.objects.get_or_create(name=name)

        for name in classifications:
            Classification.objects.get_or_create(name=name)

        # ------------------------
        # seed banks
        # ------------------------
        demo_bank, _ = Bank.objects.get_or_create(name="Demo Bank")

        # ------------------------
        # seed demo customers
        # ------------------------
        self.stdout.write("✅ Seeding demo customers...")

        customer_types = ["owner", "consultant", "commercial"]
        counter = 1000

        for customer_type in customer_types:
            for i in range(1, 6):
                counter += 1

                # create or get bank account
                bank_acc, created = BankAccount.objects.get_or_create(
                    account_number=f"12345678{counter}",
                    defaults={
                        'account_holder_name': f"Holder {counter}",
                        'iban_number': f"SA0380000000608010167{counter}",
                        'bank': demo_bank
                    }
                )

                customer, _ = Customer.objects.get_or_create(
                    customer_code=f"{customer_type[:3].upper()}-{counter}",
                    defaults={
                        "customer_type": customer_type,
                        "full_name": f"{customer_type.capitalize()} Customer {i}",
                        "birth_date": "1990-01-01",
                        "phone_number": f"050{counter}",
                        "whatsapp_number": f"051{counter}",
                        "email": f"{customer_type}{i}@example.com",
                        "status": "active",
                        "preferred_language": "en",
                        "notes": "Demo seeded customer",
                        "country": country_objs[0],
                        "city": City.objects.first(),
                        "currency": Currency.objects.first(),
                        "communication_method": CommunicationMethod.objects.first(),
                        "billing": Billing.objects.first(),
                        "bank_account": bank_acc,
                    }
                )

                if customer_type == "owner":
                    OwnerProfile.objects.get_or_create(
                        customer=customer,
                        defaults={
                            "authorized_person_name": "Authorized Person",
                            "authorized_person_email": "auth@example.com",
                            "authorized_person_phone_number": "0551234567",
                            "authorized_person_birth_date": "1990-02-02",
                            "authorized_person_address": "Authorized Address",
                            "authorized_person_national_id_number": f"99887766{counter}",
                            "authorized_person_national_id_expiry_date": "2030-01-01",
                            "authorized_person_passport_number": f"AUTHPASS{counter}",
                            "authorized_person_passport_expiry_date": "2030-01-01",
                        }
                    )

                if customer_type in ["consultant", "commercial"]:
                    company_profile, _ = CompanyProfile.objects.get_or_create(
                        customer=customer,
                        defaults={
                            "classification": Classification.objects.first(),
                            "postal_code": "12345",
                            "landline_number": f"02{counter}",
                            "company_office_address": "Company HQ",
                            "company_logo_attachment": "dummy_logo.png",
                            "company_trade_license_number": f"TL{counter}",
                            "company_trade_license_attachment": "license.pdf",
                            "company_trade_license_expiry_date": "2030-12-31",
                            "company_stamp_attachment": "stamp.png",
                            "company_establishment_date": "2010-01-01",
                            "map_location": "https://maps.google.com",
                            "area": "Sample Area",
                            "responsible_person_name": "John Doe",
                            "responsible_person_birth_date": "1985-05-20",
                            "responsible_person_address": "Home 1",
                            "responsible_person_job_title": "Manager",
                            "responsible_person_phone_number": "0539876543",
                            "responsible_person_email": "responsible@example.com",
                            "responsible_person_national_id_number": f"9988776{counter}",
                            "responsible_person_national_id_expiry_date": "2030-01-01",
                            "responsible_person_passport_number": f"RP{counter}",
                            "responsible_person_passport_expiry_date": "2030-01-01",
                        }
                    )

                    for j in range(2):
                        ContactPerson.objects.get_or_create(
                            company_profile=company_profile,
                            name=f"Contact {j + 1}",
                            defaults={
                                "job_title": "Sales",
                                "email": f"contact{j + 1}@example.com",
                                "phone_number": f"054{counter}{j}",
                                "whatsapp_number": f"056{counter}{j}",
                                "is_primary": (j == 0)
                            }
                        )

        self.stdout.write(self.style.SUCCESS("🎉 Full seed completed successfully!"))
