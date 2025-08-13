from rest_framework import serializers
from customers.models import Person
from core.serializers import BasePersonFieldsMixinSerializer
from shared.models import Gender, Nationality
from shared.serializers import GenderSerializer, NationalitySerializer


class PersonSerializer(BasePersonFieldsMixinSerializer, serializers.ModelSerializer):
    # ✅ READ: Nested full object
    gender = GenderSerializer(read_only=True)
    nationality = NationalitySerializer(read_only=True)

    # ✅ WRITE: ForeignKey ID (تربط مع الجداول)
    gender_id = serializers.PrimaryKeyRelatedField(
        queryset=Gender.objects.all(),
        source="gender",
        write_only=True,
        required=False
    )
    nationality_id = serializers.PrimaryKeyRelatedField(
        queryset=Nationality.objects.all(),
        source="nationality",
        write_only=True,
        required=False
    )

    # ✅ تواريخ بصيغة YYYY-MM-DD
    birth_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], required=False)
    passport_expiry_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], required=False)
    national_id_expiry_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], required=False)

    # ✅ نصوص عادية
    home_address = serializers.CharField(required=False, allow_blank=True)
    passport_number = serializers.CharField(required=False, allow_blank=True)
    national_id_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Person
        fields = [
            "id", "birth_date", "home_address",
            "gender", "gender_id", "nationality", "nationality_id",
            "national_id_number", "national_id_attachment", "national_id_expiry_date",
            "passport_number", "passport_attachment", "passport_expiry_date",
            "signature_attachment", "personal_image_attachment", "customer"
        ]
        read_only_fields = ["id", "customer"]

    def to_internal_value(self, data):
        # ✅ معالجة التواريخ بشكل مرن (dd/mm/yyyy → yyyy-mm-dd)
        data = data.copy()

        def parse_date(field):
            val = data.get(field)
            if isinstance(val, str):
                val = val.strip()
                if "/" in val:
                    try:
                        day, month, year = val.replace(" ", "").split("/")
                        data[field] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    except Exception:
                        pass

        for field in ["birth_date", "national_id_expiry_date", "passport_expiry_date"]:
            parse_date(field)

        return super().to_internal_value(data)
