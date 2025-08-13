from rest_framework import serializers
from approvals.models import DeleteClientRequest
from customers.serializers.customer import CustomerSerializer  # لو الهدف عميل


class DeleteRequestSerializer(serializers.ModelSerializer):
    """
    Serializer عام لطلبات الحذف.
    يعرض معلومات إضافية عن المستخدمين والهدف (target).
    """
    requested_by_username = serializers.CharField(source="requested_by.username", read_only=True)
    approved_by_username = serializers.CharField(source="approved_by.username", read_only=True)

    # لتحديد نوع الكائن المرتبط
    target_content_type = serializers.SerializerMethodField()
    target_object_repr = serializers.SerializerMethodField()

    # عرض تفاصيل العميل إن وجد
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = DeleteClientRequest
        fields = '__all__'
        read_only_fields = [
            'requested_by', 'status', 'approved_by', 'approved_at', 'created_at'
        ]

    def get_target_content_type(self, obj):
        return obj.content_type.model if obj.content_type else None

    def get_target_object_repr(self, obj):
        return str(obj.target) if obj.target else None

    def get_customer_details(self, obj):
        from backend.customers.models.models import Customer
        if isinstance(obj.target, Customer):
            return CustomerSerializer(obj.target).data
        return None
