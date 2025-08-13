from django.core.management.base import BaseCommand
from suppliers.models import ScopeOfWork, SupplierGroup

class Command(BaseCommand):
    help = "Seed Scope of Work and Supplier Groups"

    def handle(self, *args, **kwargs):
        scope, _ = ScopeOfWork.objects.get_or_create(name="Construction", description="Construction related work")
        group, _ = SupplierGroup.objects.get_or_create(name="Main Contractors", scope_of_work=scope)

        self.stdout.write(self.style.SUCCESS("✅ Seeded ScopeOfWork and SupplierGroup"))
