# customers/models/person.py
from django.db import models
from core.models import BasePerson
from customers.models.customer import Customer

class Person(BasePerson):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="person"
    )

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return self.customer.name_en or self.customer.name_ar or "Person"
