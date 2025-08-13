from django.core.management.base import BaseCommand
from customers.models import Customer, AuthorizedPerson
from shared.models import Gender, Nationality, Country, City


class Command(BaseCommand):
    help = "Seed one authorized person for first owner-type customer"

    def handle(self, *args, **kwargs):
        customer = Customer.objects.filter(customer_type="owner").first()
        if not customer:
            self.stdout.write(self.style.ERROR("❌ No owner-type customer found."))
            return

        gender = Gender.objects.first()
        nationality = Nationality.objects.first()
        country = Country.objects.first()
        city = City.objects.first()

        authorized = AuthorizedPerson.objects.create(
            customer=customer,
            name_en="John Doe",
            name_ar="جون دو",
            code="AUTH-12345",
            email="john@example.com",
            telephone_number="0501234567",
            whatsapp_number="0501234567",
            gender=gender,
            nationality=nationality,
            country=country,
            city=city,
            area="Downtown",
            birth_date="1990-01-01",
            home_address="Somewhere",
            national_id_number="1234567890",
            national_id_expiry_date="2030-01-01",
            passport_number="A1234567",
            passport_expiry_date="2030-01-01",
            power_of_attorney_expiry_date="2030-12-31"
        )

        self.stdout.write(self.style.SUCCESS(
            f"✅ AuthorizedPerson created with ID {authorized.id} for customer {customer.id}"
        ))
