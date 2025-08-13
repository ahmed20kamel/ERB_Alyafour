from django.db import models
from core.models import TrackableBase, NameCodeBase


class Country(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name_en or self.name_ar


class City(NameCodeBase, TrackableBase):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name_en or self.name_ar} - {self.country.name_en or self.country.name_ar}"


class Area(NameCodeBase, TrackableBase):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="areas")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def __str__(self):
        return f"{self.name_en or self.name_ar} - {self.city.name_en or self.city.name_ar}"


class Nationality(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"

    def __str__(self):
        return self.name_en or self.name_ar


class Gender(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gender"
        verbose_name_plural = "Genders"

    def __str__(self):
        return self.name_en or self.name_ar


class Classification(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"

    def __str__(self):
        return self.name_en or self.name_ar


class Currency(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name_en or self.name_ar


class CommunicationMethod(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Communication Method"
        verbose_name_plural = "Communication Methods"

    def __str__(self):
        return self.name_en or self.name_ar


class Billing(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Billing Method"
        verbose_name_plural = "Billing Methods"

    def __str__(self):
        return self.name_en or self.name_ar
    
# shared/models.py

from core.models import (NameCodeBase, TrackableBase)

class Language(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

class Bank(NameCodeBase, TrackableBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"

    def __str__(self):
        return self.name_en or self.name_ar
