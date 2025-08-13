from rest_framework import serializers
from customers.models import LegalPerson
from core.serializers import (
    NameCodeFieldsMixinSerializer,
    ContactInfoFieldsMixinSerializer,
    BasePersonFieldsMixinSerializer,
    TrackableFieldsMixinSerializer
)
from shared.models import Country, City, Gender, Nationality
from shared.serializers import CountrySerializer, CitySerializer, GenderSerializer, NationalitySerializer

class LegalPersonSerializer(
    NameCodeFieldsMixinSerializer,
    ContactInfoFieldsMixinSerializer,
    BasePersonFieldsMixinSerializer,
    TrackableFieldsMixinSerializer,
    serializers.ModelSerializer
):
    # 🔁 FKs
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source="country", write_only=True, required=False
    )

    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source="city", write_only=True, required=False
    )

    gender = GenderSerializer(read_only=True)
    gender_id = serializers.PrimaryKeyRelatedField(
        queryset=Gender.objects.all(), source="gender", write_only=True, required=False
    )

    nationality = NationalitySerializer(read_only=True)
    nationality_id = serializers.PrimaryKeyRelatedField(
        queryset=Nationality.objects.all(), source="nationality", write_only=True, required=False
    )

    # 🔁 ملفات
    national_id_attachment = serializers.FileField(required=False, allow_null=True)
    passport_attachment = serializers.FileField(required=False, allow_null=True)
    signature_attachment = serializers.FileField(required=False, allow_null=True)
    personal_image_attachment = serializers.ImageField(required=False, allow_null=True)
    power_of_attorney_attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = LegalPerson
        fields = "__all__"
        read_only_fields = ["id"]
        extra_kwargs = {
            "customer": {"read_only": True}  # ✅ هذا هو المطلوب لإصلاح الخطأ
        }
