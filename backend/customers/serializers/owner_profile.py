from rest_framework import serializers
from customers.models import OwnerProfile
from core.models import Gender, Nationality
from core.serializers.lookups import GenderSerializer as GenderDetailSerializer, NationalitySerializer as NationalityDetailSerializer


class OwnerProfileSerializer(serializers.ModelSerializer):
    gender = GenderDetailSerializer(read_only=True)
    nationality = NationalityDetailSerializer(read_only=True)

    # Writable foreign keys
    gender_id = serializers.PrimaryKeyRelatedField(queryset=Gender.objects.all(), source='gender', write_only=True, required=False)
    nationality_id = serializers.PrimaryKeyRelatedField(queryset=Nationality.objects.all(), source='nationality', write_only=True, required=False)

    # Optional file/image fields
    personal_image_attachment = serializers.ImageField(use_url=True, required=False, allow_null=True)
    signature_attachment = serializers.ImageField(use_url=True, required=False, allow_null=True)
    passport_attachment = serializers.FileField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = OwnerProfile
        exclude = ['customer']
