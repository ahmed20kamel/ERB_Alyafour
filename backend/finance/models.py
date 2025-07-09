from django.db import models
from approvals.models import DeleteClientRequest, UpdateRequest
from core.models import Country


class Bank(models.Model):
    name = models.CharField(max_length=150, unique=True)
    name_arabic = models.CharField(max_length=150, blank=True, null=True)
    swift_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, related_name="accounts")
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=100, unique=True)
    iban_number = models.CharField(max_length=50, blank=True, null=True)
    iban_certificate_attachment = models.FileField(upload_to='finance/iban_certificates/', blank=True, null=True)

    # علاقات مستقبلية:
    linked_customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bank_accounts"
    )

    def __str__(self):
        return f"{self.bank.name} - {self.account_holder_name}"
