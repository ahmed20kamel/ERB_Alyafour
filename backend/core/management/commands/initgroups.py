from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Initialize default user groups"

    def handle(self, *args, **kwargs):
        groups = ['employee', 'supervisor', 'manager', 'superadmin']
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group {group_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Group {group_name} already exists"))
