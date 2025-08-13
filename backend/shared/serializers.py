from rest_framework import serializers
from shared.models import (
    Country, City, Area, Nationality, Gender, Classification,
    Currency, CommunicationMethod, Billing, Language,Bank
)

# ========== Geography ==========

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name_en", "name_ar", "code"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name_en", "name_ar", "code", "country"]


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name_en", "name_ar", "code", "city"]


# ========== Other Lookups ==========

class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = ["id", "name_en", "name_ar", "code"]


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ["id", "name_en", "name_ar", "code"]


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ["id", "name_en", "name_ar", "code"]


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "name_en", "name_ar", "code"]


class CommunicationMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationMethod
        fields = ["id", "name_en", "name_ar", "code"]


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ["id", "name_en", "name_ar", "code"]
# shared/serializers.py

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name_en", "name_ar", "code"]
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["id", "name_en", "name_ar", "code"]
        