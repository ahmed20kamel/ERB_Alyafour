import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # ← عدّل المسار لو مشروعك مختلف
django.setup()

from shared.models import Country, City, Area

# === تحميل البيانات من Excel ===
file_path = "dropdown_seed_data.xlsx"  # ← تأكد أن الملف في نفس مجلد التشغيل

df_country = pd.read_excel(file_path, sheet_name="countries")
df_city = pd.read_excel(file_path, sheet_name="cities")
df_area = pd.read_excel(file_path, sheet_name="areas")

# === إضافة الدول ===
country_map = {}
for _, row in df_country.iterrows():
    country, _ = Country.objects.get_or_create(
        name_en=row["name_en"],
        name_ar=row["name_ar"],
        defaults={"is_active": True},
    )
    country_map[row["id"]] = country

# === إضافة المدن ===
city_map = {}
for _, row in df_city.iterrows():
    country = country_map.get(row["country_id"])
    if not country:
        continue
    city, _ = City.objects.get_or_create(
        name_en=row["name_en"],
        name_ar=row["name_ar"],
        country=country,
        defaults={"is_active": True},
    )
    city_map[row["id"]] = city

# === إضافة المناطق ===
for _, row in df_area.iterrows():
    city = city_map.get(row["city_id"])
    if not city:
        continue
    Area.objects.get_or_create(
        name_en=row["name_en"],
        name_ar=row["name_ar"],
        city=city,
        defaults={"is_active": True},
    )

print("✅ Seeding complete: Countries, Cities, Areas")
