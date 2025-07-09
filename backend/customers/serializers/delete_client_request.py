from rest_framework import serializers
from customers.models import DeleteClientRequest, Customer
from customers.serializers import CustomerSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class DeleteClientRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for DeleteClientRequest with customer details and user info.
    """
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    requested_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    customer_details = CustomerSerializer(source="customer", read_only=True)

    class Meta:
        model = DeleteClientRequest
        fields = [
            'id', 'customer', 'customer_details', 'requested_by', 'status',
            'comment', 'reviewed_by', 'created_at', 'reviewed_at'
        ]
        read_only_fields = [
            'status', 'reviewed_by', 'created_at', 'reviewed_at'
        ]

    def validate(self, attrs):
        """
        Ensure there is no existing pending delete request for this customer.
        """
        customer = attrs.get('customer')
        if DeleteClientRequest.objects.filter(customer=customer, status=DeleteClientRequest.STATUS_PENDING).exists():
            raise serializers.ValidationError("A delete request for this customer is already pending.")
        return attrs

    def create(self, validated_data):
        """
        Automatically attach the requesting user as requested_by.
        """
        request = self.context.get('request')
        user = request.user
        validated_data['requested_by'] = user
        return super().create(validated_data)
