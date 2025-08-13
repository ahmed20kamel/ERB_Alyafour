# customers/models/authorized_person.py

from django.db import models
from core.models import (
    NameCodeBase, TrackableBase,
    ContactInfoBase, BasePerson
)
from customers.models.customer import Customer
class AuthorizedPerson(
    NameCodeBase,
    TrackableBase,
    ContactInfoBase,
    BasePerson
):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="authorized_people")


    power_of_attorney_attachment = models.FileField(
        upload_to='authorized/poa/',
        blank=True, null=True
    )

    power_of_attorney_expiry_date = models.DateField(
        blank=True, null=True
    )

    def __str__(self):
        return self.customer.name_en or self.customer.name_ar or "Authorized Person"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.customer.customer_type != 'owner':
            raise ValidationError("AuthorizedPerson is only valid for owner customers.")
