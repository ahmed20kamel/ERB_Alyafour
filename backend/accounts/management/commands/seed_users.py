from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create default users with different permissions."

    def handle(self, *args, **options):
        # سوبر أدمن
        if not User.objects.filter(username="ahmed").exists():
            User.objects.create_superuser(
                username="ahmed",
                email="ahmed@example.com",
                password="Yaf@12345$"
            )
            self.stdout.write(self.style.SUCCESS("✅ Superuser 'ahmed' created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Superuser 'ahmed' already exists."))

        # موظف عادي staff
        if not User.objects.filter(username="staff_user").exists():
            User.objects.create_user(
                username="staff_user",
                email="staff@example.com",
                password="Staff@1234",
                is_staff=True,
                is_superuser=False
            )
            self.stdout.write(self.style.SUCCESS("✅ Staff user created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Staff user already exists."))

        # موظف غير إداري (عادي تمامًا)
        if not User.objects.filter(username="normal_user").exists():
            User.objects.create_user(
                username="normal_user",
                email="user@example.com",
                password="User@1234",
                is_staff=False,
                is_superuser=False
            )
            self.stdout.write(self.style.SUCCESS("✅ Normal user created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Normal user already exists."))
