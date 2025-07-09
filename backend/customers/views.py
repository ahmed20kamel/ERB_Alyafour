from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from customers.models import Customer
from customers.serializers.customer import CustomerSerializer
from approvals.models import DeleteClientRequest

# لوك أب موديلات وسيريالايزرز
from core.models import (
    Country, City, Nationality, Gender,
    Currency, CommunicationMethod, Billing, Classification,
)
from core.serializers.lookups import (
    CountrySerializer, CitySerializer, NationalitySerializer, GenderSerializer,
    CurrencySerializer, CommunicationMethodSerializer, BillingSerializer, ClassificationSerializer
)

from django.db.models import Count


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(deleted_at__isnull=True).order_by('-id')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer_type']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("🔴 Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()

        if customer.delete_requested:
            return Response({"message": "Delete already requested."}, status=400)

        DeleteClientRequest.objects.create(
            customer=customer,
            requested_by=request.user
        )

        customer.delete_requested = True
        customer.save()

        return Response({"message": "Delete request created, waiting for approval."}, status=202)

    @action(detail=True, methods=["post"])
    def approve_delete(self, request, pk=None):
        customer = self.get_object()
        try:
            delete_request = DeleteClientRequest.objects.get(customer=customer, status="pending")
            delete_request.approve(manager_user=request.user)
            return Response({"message": "Customer deletion approved and soft-deleted."})
        except DeleteClientRequest.DoesNotExist:
            return Response({"error": "No pending delete request found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["post"])
    def reject_delete(self, request, pk=None):
        customer = self.get_object()
        try:
            delete_request = DeleteClientRequest.objects.get(customer=customer, status="pending")
            reason = request.data.get("reason", "تم الرفض من CustomerViewSet")
            delete_request.reject(manager_user=request.user, comment=reason)

            customer.delete_requested = False
            customer.save()

            return Response({"message": "Customer delete request rejected."})
        except DeleteClientRequest.DoesNotExist:
            return Response({"error": "No pending delete request found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# ✅ Lookup ViewSets
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.order_by('id')
    serializer_class = CountrySerializer

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.order_by('id')
    serializer_class = CitySerializer

class NationalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Nationality.objects.order_by('id')
    serializer_class = NationalitySerializer

class GenderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gender.objects.order_by('id')
    serializer_class = GenderSerializer

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.order_by('id')
    serializer_class = CurrencySerializer

class CommunicationMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationMethod.objects.order_by('id')
    serializer_class = CommunicationMethodSerializer

class BillingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Billing.objects.order_by('id')
    serializer_class = BillingSerializer

class ClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Classification.objects.order_by('id')
    serializer_class = ClassificationSerializer


@api_view(['GET'])
def customer_dashboard_stats(request):
    one_week_ago = timezone.now() - timezone.timedelta(days=7)

    total_customers = Customer.objects.filter(deleted_at__isnull=True).count()
    added_recently_count = Customer.objects.filter(
        created_at__gte=one_week_ago,
        deleted_at__isnull=True
    ).count()

    deleted_recently_count = Customer.objects.filter(
        deleted_at__gte=one_week_ago
    ).count()

    counts = Customer.objects.filter(deleted_at__isnull=True).values('customer_type').annotate(total=Count('id'))

    type_counts = {'owner': 0, 'consultant': 0, 'commercial': 0}
    for item in counts:
        type_counts[item['customer_type']] = item['total']

    recently_added = Customer.objects.filter(
        created_at__gte=one_week_ago,
        deleted_at__isnull=True
    ).values('id', 'full_name_english', 'created_at')

    recently_deleted = Customer.objects.filter(
        deleted_at__gte=one_week_ago
    ).values('id', 'full_name_english', 'deleted_at')

    return Response({
        "total_customers": total_customers,
        "added_recently": added_recently_count,
        "deleted_recently": deleted_recently_count,
        "counts_by_type": type_counts,
        "recently_added": list(recently_added),
        "recently_deleted": list(recently_deleted),
    })
