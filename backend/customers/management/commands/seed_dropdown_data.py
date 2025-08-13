from django.core.management.base import BaseCommand
from shared.models import Country, City, Area


class Command(BaseCommand):
    help = "Seeds countries, cities, and areas without Excel"

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Deleting old records...")
        Area.objects.all().delete()
        City.objects.all().delete()
        Country.objects.all().delete()

        self.stdout.write("🚀 Seeding data...")

        for c_index in range(1, 11):
            country = Country.objects.create(
                name_en=f"Country {c_index} EN",
                name_ar=f"الدولة {c_index}",
                code=f"CTR-{c_index:02}",
                is_active=True,
            )

            for ci_index in range(1, 3):  # 2 cities per country
                city = City.objects.create(
                    country=country,
                    name_en=f"City {ci_index} of Country {c_index} EN",
                    name_ar=f"مدينة {ci_index} من الدولة {c_index}",
                    code=f"CITY-{c_index:02}-{ci_index:02}",
                    is_active=True,
                )

                for a_index in range(1, 4):  # 3 areas per city
                    Area.objects.create(
                        city=city,
                        name_en=f"Area {a_index} of City {ci_index}, Country {c_index} EN",
                        name_ar=f"المنطقة {a_index} من المدينة {ci_index} الدولة {c_index}",
                        code=f"AREA-{c_index:02}-{ci_index:02}-{a_index:02}",
                        is_active=True,
                    )

        self.stdout.write(self.style.SUCCESS("✅ Done seeding 10 countries × 2 cities × 3 areas each"))
