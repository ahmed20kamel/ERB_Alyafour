# customers/models/legal_person.py

from django.db import models
from core.models import (
    NameCodeBase, TrackableBase,
    ContactInfoBase, BasePerson
)
from customers.models.customer import Customer


class LegalPerson(
    NameCodeBase,
    TrackableBase,
    ContactInfoBase,
    BasePerson
):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="legal_person"
    )

    power_of_attorney_attachment = models.FileField(
        upload_to='legal/poa/',
        blank=True, null=True
    )

    power_of_attorney_expiry_date = models.DateField(
        blank=True, null=True
    )

def __str__(self):
    return self.customer.name_en or self.customer.name_ar or "Legal Person"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.customer.customer_type not in ['commercial', 'consultant']:
            raise ValidationError("LegalPerson is only allowed for commercial or consultant customers.")
