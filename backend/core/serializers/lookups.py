from rest_framework import serializers
from core.models import (
    Country, City, Nationality, Gender,
    Currency, CommunicationMethod, Billing, Classification
)

"""
Simple lookup serializers for drop-down lists.
"""

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = ['id', 'name']

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'name']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name']

class CommunicationMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationMethod
        fields = ['id', 'name']

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ['id', 'name']

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ['id', 'name']
