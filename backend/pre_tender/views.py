from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Tender, Answer, TenderFile, TenderFieldOverride, TenderCustomField
from .serializers import (
    TenderCreateSerializer, TenderListItemSerializer, TenderDetailSerializer,
    AnswerUpsertSerializer, OverrideSerializer, CustomFieldSerializer
)

class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # عندك في settings الافتراضي AllowAny؛ عدّل الصلاحيات زي ما تحب
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_authenticated

# 1) إنشاء تندر + snapshot
class TenderCreateAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def post(self, request):
        ser = TenderCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        tender = Tender.create_with_snapshot(
            user=request.user if request.user.is_authenticated else None,
            title=ser.validated_data["title"],
            meta=ser.validated_data.get("meta") or {},
        )
        return Response(TenderDetailSerializer(tender).data, status=status.HTTP_201_CREATED)

# 2) قائمة/تفاصيل
class TenderListAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def get(self, request):
        qs = Tender.objects.order_by("-created_at")
        data = TenderListItemSerializer(qs, many=True).data
        return Response(data)

class TenderDetailAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def get(self, request, pk):
        tender = get_object_or_404(Tender, pk=pk)
        return Response(TenderDetailSerializer(tender).data)

# 3) كتابة إجابات + ملفات
class TenderAnswersAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    @transaction.atomic
    def post(self, request, pk):
        """
        payload:
        {
          "answers": [{ "field_key": "contractor_name", "value": "..." }, ...]
        }
        وملفات via multipart بنفس أسماء field_key (يدعم متعددة)
        """
        tender = get_object_or_404(Tender, pk=pk)
        if tender.status not in ("draft", "submitted"):
            return Response({"detail": "Tender is locked."}, status=400)

        answers = request.data.get("answers", [])
        if not isinstance(answers, list):
            return Response({"detail": "answers must be a list."}, status=400)

        # Index snapshot
        snap_index = {}
        for sec in tender.schema_snapshot.get("sections", []):
            for fd in sec.get("fields", []):
                if fd.get("enabled", True):
                    snap_index[fd["key"]] = fd

        for item in answers:
            ser = AnswerUpsertSerializer(data=item)
            ser.is_valid(raise_exception=True)
            key = ser.validated_data["field_key"]
            val = ser.validated_data["value"]
            fd = snap_index.get(key)
            if not fd:
                return Response({"detail": f"Unknown field_key '{key}' for this tender."}, status=400)
            Answer.objects.update_or_create(
                tender=tender, field_key=key,
                defaults={
                    "value": val,
                    "label_at_submit": fd["label"],
                    "type_at_submit": fd["type"],
                }
            )

        for field_key in request.FILES:
            for f in request.FILES.getlist(field_key):
                TenderFile.objects.create(
                    tender=tender,
                    field_key=field_key,
                    file=f,
                    name=f.name
                )

        return Response({"status": "ok"})

# 4) Submit
class TenderSubmitAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def post(self, request, pk):
        tender = get_object_or_404(Tender, pk=pk)
        if tender.status != "draft":
            return Response({"detail": "Already submitted or closed."}, status=400)
        tender.status = "submitted"
        tender.save(update_fields=["status"])
        return Response({"status": "submitted"})

# 5) Approve/Reject
class TenderApproveAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def post(self, request, pk):
        tender = get_object_or_404(Tender, pk=pk)
        tender.status = "approved"
        tender.save(update_fields=["status"])
        return Response({"status": "approved"})

class TenderRejectAPI(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def post(self, request, pk):
        tender = get_object_or_404(Tender, pk=pk)
        tender.status = "rejected"
        tender.save(update_fields=["status"])
        return Response({"status": "rejected"})

# 6) Overrides/CustomFields (للأدمن) + إعادة بناء Snapshot
class TenderOverridesAPI(APIView):
    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def post(self, request, pk):
        tender = get_object_or_404(Tender, pk=pk)
        if tender.status != "draft":
            return Response({"detail": "Cannot change overrides on non-draft."}, status=400)

        overrides = request.data.get("overrides", [])
        customs = request.data.get("custom_fields", [])

        for item in overrides:
            ser = OverrideSerializer(data=item)
            ser.is_valid(raise_exception=True)
            TenderFieldOverride.objects.update_or_create(
                tender=tender, field_key=ser.validated_data["field_key"],
                defaults={k: v for k, v in ser.validated_data.items() if k != "field_key"}
            )

        for item in customs:
            ser = CustomFieldSerializer(data=item)
            ser.is_valid(raise_exception=True)
            TenderCustomField.objects.update_or_create(
                tender=tender, field_key=ser.validated_data["field_key"],
                defaults={k: v for k, v in ser.validated_data.items() if k != "field_key"}
            )

        tender.rebuild_snapshot()
        return Response({"status": "snapshot_rebuilt", "schema_snapshot": tender.schema_snapshot})
