from django.db import models
from core.models import (NameCodeBase, TrackableBase, ContactInfoBase)
from customers.models.customer import Customer

class ContactPerson(NameCodeBase, TrackableBase, ContactInfoBase):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="contact_people"
    )
    job_title = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.name_en or self.customer.name_ar or "Contact Person"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.customer.customer_type not in ['commercial', 'consultant']:
            raise ValidationError("ContactPerson is only allowed for commercial or consultant customers.")
