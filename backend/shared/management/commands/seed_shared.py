from django.core.management.base import BaseCommand
from shared.models import Country, City, Area, Bank

class Command(BaseCommand):
    help = "Seed countries, cities, banks"

    def handle(self, *args, **kwargs):
        country, _ = Country.objects.get_or_create(name_ar="الإمارات", name_en="UAE", code="AE")
        city, _ = City.objects.get_or_create(name_ar="أبوظبي", name_en="Abu Dhabi", code="AUH", country=country)
        area, _ = Area.objects.get_or_create(name_ar="المرور", name_en="Al Muroor", code="AUH-MUR", city=city)

        bank, _ = Bank.objects.get_or_create(name_ar="بنك أبوظبي الأول", name_en="FAB", code="BANK-FAB")

        self.stdout.write(self.style.SUCCESS("✅ Seeded Country, City, Area, Bank"))
