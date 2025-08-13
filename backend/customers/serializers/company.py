from rest_framework import serializers
from customers.models import Company
from core.serializers import BaseCompanyFieldsMixinSerializer
from shared.models import Classification, Country, City
from shared.serializers import ClassificationSerializer, CountrySerializer, CitySerializer

class CompanySerializer(
    BaseCompanyFieldsMixinSerializer,
    serializers.ModelSerializer
):
    # 🔁 العلاقات Foreign Keys
    classification = ClassificationSerializer(read_only=True)
    classification_id = serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(),
        source="classification",
        write_only=True,
        required=False
    )

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

    # 🔁 مرفقات الملفات
    logo_attachment = serializers.ImageField(required=False, allow_null=True)
    stamp_attachment = serializers.FileField(required=False, allow_null=True)
    trade_license_attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id"]
        extra_kwargs = {
            "customer": {"read_only": True}  # ✅ هذا هو المطلوب لإصلاح الخطأ
        }
