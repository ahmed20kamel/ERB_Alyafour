from rest_framework import serializers
from shared.serializers import CountrySerializer, CitySerializer, ClassificationSerializer, GenderSerializer, NationalitySerializer, BankSerializer


# ========== Name & Code Base ==========
class NameCodeFieldsMixinSerializer(serializers.Serializer):
    name_ar = serializers.CharField()
    name_en = serializers.CharField()
    code = serializers.CharField(read_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)


# ========== Trackable Base ==========
class TrackableFieldsMixinSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
    deleted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
    delete_requested = serializers.BooleanField(required=False, default=False)



# ========== Contact Info Base ==========
class ContactInfoFieldsMixinSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    telephone_number = serializers.CharField(required=False, allow_blank=True)
    whatsapp_number = serializers.CharField(required=False, allow_blank=True)

    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=CountrySerializer.Meta.model.objects.all(),
        source="country",
        write_only=True,
        required=False
    )

    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=CitySerializer.Meta.model.objects.all(),
        source="city",
        write_only=True,
        required=False
    )

    area = serializers.CharField(required=False, allow_blank=True)


# ========== Bank Account Base ==========
class BankAccountFieldsMixinSerializer(serializers.Serializer):
    bank = BankSerializer(read_only=True)
    bank_id = serializers.PrimaryKeyRelatedField(
        queryset=BankSerializer.Meta.model.objects.all(),
        source="bank",
        write_only=True,
        required=False
    )
    account_holder_name = serializers.CharField(required=False, allow_blank=True)
    account_number = serializers.CharField(required=False, allow_blank=True)
    iban_number = serializers.CharField(required=False, allow_blank=True)
    iban_certificate = serializers.FileField(required=False)


# ========== Base Person ==========
class BasePersonFieldsMixinSerializer(serializers.Serializer):
    birth_date = serializers.DateField(required=False)
    home_address = serializers.CharField(required=False, allow_blank=True)

    gender = GenderSerializer(read_only=True)
    gender_id = serializers.PrimaryKeyRelatedField(
        queryset=GenderSerializer.Meta.model.objects.all(),
        source="gender",
        write_only=True,
        required=False
    )

    nationality = NationalitySerializer(read_only=True)
    nationality_id = serializers.PrimaryKeyRelatedField(
        queryset=NationalitySerializer.Meta.model.objects.all(),
        source="nationality",
        write_only=True,
        required=False
    )

    national_id_number = serializers.CharField(required=False, allow_blank=True)
    national_id_attachment = serializers.FileField(required=False)
    national_id_expiry_date = serializers.DateField(required=False)

    passport_number = serializers.CharField(required=False, allow_blank=True)
    passport_attachment = serializers.FileField(required=False)
    passport_expiry_date = serializers.DateField(required=False)

    signature_attachment = serializers.FileField(required=False)
    personal_image_attachment = serializers.ImageField(required=False)


# ========== Base Company ==========
class BaseCompanyFieldsMixinSerializer(serializers.Serializer):
    trade_license_number = serializers.CharField(required=False, allow_blank=True)
    trade_license_expiry_date = serializers.DateField(required=False)
    trade_license_attachment = serializers.FileField(required=False)

    stamp_attachment = serializers.ImageField(required=False)
    logo_attachment = serializers.ImageField(required=False)

    classification = ClassificationSerializer(read_only=True)
    classification_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassificationSerializer.Meta.model.objects.all(),
        source="classification",
        write_only=True,
        required=False
    )

    postal_code = serializers.CharField(required=False, allow_blank=True)
    landline_number = serializers.CharField(required=False, allow_blank=True)
    office_address = serializers.CharField(required=False, allow_blank=True)
    map_location = serializers.URLField(required=False, allow_blank=True)
    establishment_date = serializers.DateField(required=False)
    company_fax = serializers.CharField(required=False, allow_blank=True)