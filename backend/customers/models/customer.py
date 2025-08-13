# customers/models/customer.py
from django.db import models
from core.models import (
    NameCodeBase, TrackableBase,
    ContactInfoBase, BankAccountBase
)

class Customer(NameCodeBase, TrackableBase, ContactInfoBase, BankAccountBase):
    CUSTOMER_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('commercial', 'Commercial'),
        ('consultant', 'Consultant'),
    ]

    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES)
    status = models.CharField(max_length=20, default='active')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.customer_type == 'owner' and not hasattr(self, 'person'):
            raise ValidationError("Owner customer must have a related person.")

        if self.customer_type in ['commercial', 'consultant'] and not hasattr(self, 'company'):
            raise ValidationError("Commercial/Consultant customer must have a related company.")

        if hasattr(self, 'person') and hasattr(self, 'company'):
            raise ValidationError("Customer can be linked to either person or company, not both.")

    def __str__(self):
        return f"{self.code} - {self.name_en or self.name_ar}"
