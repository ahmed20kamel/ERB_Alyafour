# apps/customers/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from django.utils.timezone import now
from datetime import timedelta

from customers.models import (
    Customer, Person, Company,
    AuthorizedPerson, ContactPerson, LegalPerson
)
from customers.serializers import (
    CustomerSerializer, PersonSerializer, CompanySerializer,
    AuthorizedPersonSerializer, ContactPersonSerializer, LegalPersonSerializer
)


# ======================== Customer ========================
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_deleted=False).select_related(
        # شخص المالك
        "person", "person__gender", "person__nationality",
        # بيانات الشركة
        "company",
        # الشخص القانوني + علاقاته
        "legal_person", "legal_person__gender", "legal_person__nationality",
        "legal_person__country", "legal_person__city",
        # بيانات البنك والموقع
        "bank", "country", "city"
    ).prefetch_related("authorized_people", "contact_people")

    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["customer_type", "status"]
    parser_classes = [MultiPartParser, FormParser]  # مهم لـ FormData

    def create(self, request, *args, **kwargs):
        # تفضل زي ما هي
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        return Response(self.get_serializer(customer).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        ✅ نعمل PATCH/PUT جزئي بدون ما نمرّر request.data للـ serializer.is_valid(),
        لأن CustomerSerializer.update أصلاً بيقرأ request.data/FILES ويفكّ المفاتيح المسطّحة.
        ده بيمنع 400 الناتج عن مفاتيح غير معرّفة في الـ serializer.
        """
        partial = kwargs.pop("partial", True)  # خليه partial افتراضيًا
        instance = self.get_object()

        # ما نبعتش request.data للـ serializer — نخليه فاضي
        serializer = self.get_serializer(instance, data={}, partial=partial)
        serializer.is_valid(raise_exception=False)  # مفيش حاجة تتحقق هنا

        instance = serializer.save()  # هيدخل CustomerSerializer.update ويقرأ request.data
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)


# ======================== Person ========================
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [AllowAny]


# ======================== Company ========================
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]


# ======================== Authorized Person ========================
class AuthorizedPersonViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorizedPersonSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["customer"]

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_pk")
        if customer_id:
            return AuthorizedPerson.objects.filter(customer_id=customer_id, is_deleted=False).order_by("-id")
        return AuthorizedPerson.objects.filter(is_deleted=False).order_by("-id")


# ======================== Contact Person ========================
class ContactPersonViewSet(viewsets.ModelViewSet):
    serializer_class = ContactPersonSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["customer", "is_primary"]

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_pk")
        if customer_id:
            return ContactPerson.objects.filter(customer_id=customer_id, is_deleted=False).order_by("-id")
        return ContactPerson.objects.filter(is_deleted=False).order_by("-id")


# ======================== Legal Person ========================
class LegalPersonViewSet(viewsets.ModelViewSet):
    serializer_class = LegalPersonSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_pk")
        if customer_id:
            return LegalPerson.objects.filter(customer_id=customer_id)
        return LegalPerson.objects.all()


# ======================== Dashboard Stats Endpoint ========================
@api_view(["GET"])
def customer_dashboard_stats(request):
    total = Customer.objects.filter(is_deleted=False).count()

    last_week = now() - timedelta(days=7)
    added_recently = Customer.objects.filter(is_deleted=False, created_at__gte=last_week).count()
    deleted_recently = Customer.objects.filter(is_deleted=True, updated_at__gte=last_week).count()

    counts_by_type = {
        "owner": Customer.objects.filter(is_deleted=False, customer_type="owner").count(),
        "commercial": Customer.objects.filter(is_deleted=False, customer_type="commercial").count(),
        "consultant": Customer.objects.filter(is_deleted=False, customer_type="consultant").count(),
    }

    return Response({
        "total_customers": total,
        "added_recently": added_recently,
        "deleted_recently": deleted_recently,
        "counts_by_type": counts_by_type,
    })
