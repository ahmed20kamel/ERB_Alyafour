from rest_framework import serializers
from .models import (
    Supplier, SupplierGroup, ScopeOfWork,
    SupplierContactPerson, SupplierLegalPerson
)
from core.serializers import (
    NameCodeFieldsMixinSerializer, TrackableFieldsMixinSerializer,
    ContactInfoFieldsMixinSerializer, BankAccountFieldsMixinSerializer,
    BasePersonFieldsMixinSerializer, BaseCompanyFieldsMixinSerializer,
)

# -------- ScopeOfWork --------
class ScopeOfWorkSerializer(NameCodeFieldsMixinSerializer,
                            TrackableFieldsMixinSerializer,
                            serializers.ModelSerializer):
    class Meta:
        model = ScopeOfWork
        fields = "__all__"


# -------- SupplierGroup --------
class SupplierGroupSerializer(NameCodeFieldsMixinSerializer,
                              TrackableFieldsMixinSerializer,
                              serializers.ModelSerializer):
    scope_of_work = ScopeOfWorkSerializer(read_only=True)
    scope_of_work_id = serializers.PrimaryKeyRelatedField(
        queryset=ScopeOfWork.objects.all(),
        source="scope_of_work",
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = SupplierGroup
        fields = "__all__"


# -------- SupplierContactPerson --------
class SupplierContactPersonSerializer(NameCodeFieldsMixinSerializer,
                                      TrackableFieldsMixinSerializer,
                                      ContactInfoFieldsMixinSerializer,
                                      serializers.ModelSerializer):
    class Meta:
        model = SupplierContactPerson
        fields = "__all__"


# -------- SupplierLegalPerson --------
class SupplierLegalPersonSerializer(NameCodeFieldsMixinSerializer,
                                    TrackableFieldsMixinSerializer,
                                    ContactInfoFieldsMixinSerializer,
                                    BasePersonFieldsMixinSerializer,
                                    serializers.ModelSerializer):
    class Meta:
        model = SupplierLegalPerson
        fields = "__all__"


# -------- Supplier --------
class SupplierSerializer(NameCodeFieldsMixinSerializer,
                         TrackableFieldsMixinSerializer,
                         ContactInfoFieldsMixinSerializer,
                         BaseCompanyFieldsMixinSerializer,
                         BankAccountFieldsMixinSerializer,
                         serializers.ModelSerializer):
    scope_of_work = ScopeOfWorkSerializer(read_only=True)
    scope_of_work_id = serializers.PrimaryKeyRelatedField(
        queryset=ScopeOfWork.objects.all(),
        source="scope_of_work",
        write_only=True, required=False, allow_null=True
    )

    supplier_groups = SupplierGroupSerializer(many=True, read_only=True)
    supplier_group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SupplierGroup.objects.all(),
        source="supplier_groups",
        write_only=True, required=False
    )

    # ملخص الأشخاص
    contact_people = SupplierContactPersonSerializer(many=True, read_only=True)
    legal_person = SupplierLegalPersonSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = "__all__"
