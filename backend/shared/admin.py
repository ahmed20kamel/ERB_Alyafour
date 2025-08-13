from django.contrib import admin
from shared.models import (
    Country, City, Area, Nationality, Gender, Classification,
    Currency, CommunicationMethod, Billing, Language, Bank
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "is_active"]
    search_fields = ["name_en", "name_ar", "code"]
    list_filter = ["is_active"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "country", "is_active"]
    search_fields = ["name_en", "name_ar", "code"]
    list_filter = ["country", "is_active"]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "city", "is_active"]
    search_fields = ["name_en", "name_ar", "code"]
    list_filter = ["city", "is_active"]


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "is_active"]
    search_fields = ["name_en", "name_ar"]
    list_filter = ["is_active"]


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "is_active"]
    search_fields = ["name_en", "name_ar"]
    list_filter = ["is_active"]


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "is_active"]
    search_fields = ["name_en", "name_ar"]
    list_filter = ["is_active"]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "is_active"]
    search_fields = ["name_en", "name_ar", "code"]
    list_filter = ["is_active"]


@admin.register(CommunicationMethod)
class CommunicationMethodAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "is_active"]
    search_fields = ["name_en", "name_ar"]
    list_filter = ["is_active"]


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "is_active"]
    search_fields = ["name_en", "name_ar"]
    list_filter = ["is_active"]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "is_active"]
    search_fields = ["name_en", "name_ar", "code"]
    list_filter = ["is_active"]


