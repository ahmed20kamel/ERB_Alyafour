from django.core.management.base import BaseCommand
from core.models import (
    Country, City, Nationality, Gender,
    Currency, CommunicationMethod, Billing, Classification
)

class Command(BaseCommand):
    help = "Seed the database with initial lookup data."

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Seeding lookup data...")

        countries = ["Egypt", "UAE", "Saudi Arabia", "USA", "Germany"]
        cities_by_country = {
            "Egypt": ["Cairo", "Alexandria"],
            "UAE": ["Dubai", "Abu Dhabi"],
            "Saudi Arabia": ["Riyadh", "Jeddah"],
            "USA": ["New York", "Los Angeles"],
            "Germany": ["Berlin", "Munich"],
        }
        nationalities = ["Egyptian", "Emirati", "Saudi", "American", "German"]
        genders = ["Male", "Female", "Other"]
        currencies = ["EGP", "AED", "SAR", "USD", "EUR"]
        communication_methods = ["Email", "Phone", "WhatsApp"]
        billings = ["Monthly", "Quarterly", "Yearly"]
        classifications = ["A", "B", "C"]

        country_objs = {}
        for name in countries:
            country, _ = Country.objects.get_or_create(name=name)
            country_objs[name] = country

        for country_name, city_list in cities_by_country.items():
            for city_name in city_list:
                City.objects.get_or_create(name=city_name, country=country_objs[country_name])

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

        self.stdout.write(self.style.SUCCESS("✅ Lookup data seeded successfully."))
