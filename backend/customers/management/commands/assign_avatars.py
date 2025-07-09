import os
from django.core.files import File
from django.core.management.base import BaseCommand
from customers.models import Customer
from django.conf import settings


class Command(BaseCommand):
    help = 'Assign avatar images from local folder to customers'

    def handle(self, *args, **options):
        folder_path = os.path.join(settings.BASE_DIR, 'assets', 'avatars')
        images = sorted(os.listdir(folder_path))

        if not images:
            self.stdout.write(self.style.ERROR("No images found in the avatars folder."))
            return

        customers = Customer.objects.all().order_by('id')[:len(images)]

        for i, customer in enumerate(customers):
            image_path = os.path.join(folder_path, images[i])
            if not os.path.isfile(image_path):
                self.stdout.write(self.style.WARNING(f"❌ Image not found: {image_path}"))
                continue

            with open(image_path, 'rb') as img_file:
                django_file = File(img_file)

                if customer.customer_type == "owner" and customer.owner_profile:
                    customer.owner_profile.personal_image_attachment.save(images[i], django_file, save=True)
                    self.stdout.write(f"✅ Set avatar for OWNER #{customer.id}")
                elif customer.customer_type in ["consultant", "commercial"] and customer.company_profile:
                    customer.company_profile.company_logo_attachment.save(images[i], django_file, save=True)
                    self.stdout.write(f"✅ Set logo for COMPANY #{customer.id}")
                else:
                    self.stdout.write(f"⚠️ Customer #{customer.id} has no profile to attach image.")

        self.stdout.write(self.style.SUCCESS("🎉 Avatar assignment completed!"))
