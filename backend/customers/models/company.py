# customers/models/company.py
from django.db import models
from core.models import BaseCompany
from customers.models.customer import Customer

class Company(BaseCompany):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="company"
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

def __str__(self):
    return self.customer.name_en or self.customer.name_ar or "Company"

