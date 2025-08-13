from customers.serializers import (
    CustomerSerializer,
    PersonSerializer,
    CompanySerializer,
    LegalPersonSerializer,
    AuthorizedPersonSerializer,
    ContactPersonSerializer
)

from customers.models import Customer

fields = []

# Base Customer fields (flat ones)
customer_fields = [
    "id", "code", "name_ar", "name_en", "email", "telephone_number", "whatsapp_number",
    "country", "city", "area", "notes", "bank",
    "account_holder_name", "account_number", "iban_number", "iban_certificate",
    "customer_type"
]
fields.extend(customer_fields)

# Owner-specific (person) fields
fields.extend(["person_" + f for f in PersonSerializer().fields if f not in ['id']])

# Company-specific fields
fields.extend(["company_" + f for f in CompanySerializer().fields if f not in ['id']])

# Legal Person
fields.extend(["legal_person_" + f for f in LegalPersonSerializer().fields if f not in ['id']])

# Authorized People
fields.extend(["authorized_people[0]." + f for f in AuthorizedPersonSerializer().fields if f not in ['id', 'customer']])

# Contact People
fields.extend(["contact_people[0]." + f for f in ContactPersonSerializer().fields if f not in ['id', 'customer']])

# Output to file
with open("backend_fields.txt", "w", encoding="utf-8") as f:
    for field in fields:
        f.write(field + "\n")
