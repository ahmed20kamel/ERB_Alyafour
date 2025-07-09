from rest_framework import serializers
from customers.models import ContactPerson


class ContactPersonSerializer(serializers.ModelSerializer):
    """
    Serializer for contact people under company profile.
    company_profile field is handled by the parent CompanyProfile serializer.
    """

    class Meta:
        model = ContactPerson
        exclude = ['company_profile']  # لأنه بيتدار من Parent Serializer
        read_only_fields = ['id']
