from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from customers.models import CompanyProfile
from core.models import Classification
from .contact_person import ContactPersonSerializer

from core.serializers.lookups import ClassificationSerializer as ClassificationDetailSerializer


class CompanyProfileSerializer(WritableNestedModelSerializer):
    contact_people = ContactPersonSerializer(many=True, required=False, allow_null=True)

    # Read-only full classification details
    classification_detail = ClassificationDetailSerializer(source='classification', read_only=True)

    # Writeable foreign key
    classification = serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(),
        required=False
    )

    class Meta:
        model = CompanyProfile
        exclude = ['customer']  # Linked from parent serializer
        # optional: يمكن تضمين read_only_fields لو حبيت
