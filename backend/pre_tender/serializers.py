from rest_framework import serializers
from .models import Tender, Answer, TenderFile, TenderFieldOverride, TenderCustomField

class TenderCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    meta = serializers.JSONField(required=False)

class TenderListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = ["id", "code", "title", "status", "created_by", "created_at"]

class TenderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = ["id", "code", "title", "status", "created_by", "created_at", "schema_snapshot", "meta"]

class AnswerUpsertSerializer(serializers.Serializer):
    field_key = serializers.SlugField(max_length=120)
    value = serializers.JSONField(allow_null=True)

class OverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderFieldOverride
        fields = ["field_key", "enabled", "label", "required", "order", "config"]

class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderCustomField
        fields = ["section_title", "field_key", "label", "type", "required", "order", "config", "options"]
