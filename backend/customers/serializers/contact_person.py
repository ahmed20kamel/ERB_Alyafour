from rest_framework import serializers
from customers.models import ContactPerson
from core.serializers import (
    NameCodeFieldsMixinSerializer,
    ContactInfoFieldsMixinSerializer,
    TrackableFieldsMixinSerializer
)
from shared.models import Country, City
from shared.serializers import CountrySerializer, CitySerializer

class ContactPersonSerializer(
    NameCodeFieldsMixinSerializer,
    ContactInfoFieldsMixinSerializer,
    TrackableFieldsMixinSerializer,
    serializers.ModelSerializer
):
    # 🔁 FKs
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source="country",
        write_only=True,
        required=False
    )

    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source="city",
        write_only=True,
        required=False
    )

    class Meta:
        model = ContactPerson
        fields = "__all__"
        read_only_fields = ["id"]
        extra_kwargs = {
            "customer": {"read_only": True}  # ✅ هذا هو المطلوب لإصلاح الخطأ
        }
