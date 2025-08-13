from rest_framework import serializers
from customers.models import Customer
from core.serializers import TrackableFieldsMixinSerializer
from shared.models import Country, City, Bank,Area
from shared.serializers import CountrySerializer, CitySerializer, BankSerializer, AreaSerializer
from customers.serializers.person import PersonSerializer
from customers.serializers.company import CompanySerializer
from customers.serializers.legal_person import LegalPersonSerializer
from customers.serializers.contact_person import ContactPersonSerializer
from customers.serializers.authorized_person import AuthorizedPersonSerializer

class CustomerSerializer(TrackableFieldsMixinSerializer, serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    legal_person = LegalPersonSerializer(read_only=True)
    contact_people = ContactPersonSerializer(many=True, read_only=True)
    authorized_people = AuthorizedPersonSerializer(many=True, read_only=True)

    bank = BankSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    area = AreaSerializer(read_only=True)
    

    class Meta:
        model = Customer
        fields = [
            "id", "code", "name_ar", "name_en", "email",
            "telephone_number", "whatsapp_number", "country", "city", "area",
            "notes", "bank", "account_holder_name", "account_number",
            "iban_number", "iban_certificate", "customer_type",
            "person", "company", "legal_person", "contact_people", "authorized_people"
        ]
        read_only_fields = ["id", "code", "person", "company", "legal_person", "contact_people", "authorized_people"]

    def create(self, validated_data):
        request = self.context.get("request")
        data = request.data
        files = request.FILES

        customer_data = {
            "name_ar": data.get("name_ar"),
            "name_en": data.get("name_en"),
            "email": data.get("email"),
            "telephone_number": data.get("telephone_number"),
            "whatsapp_number": data.get("whatsapp_number"),
            "area": data.get("area"),
            "notes": data.get("notes"),
            "account_holder_name": data.get("account_holder_name"),
            "account_number": data.get("account_number"),
            "iban_number": data.get("iban_number"),
            "iban_certificate": files.get("iban_certificate"),
            "customer_type": data.get("customer_type"),
        }

        if data.get("bank"):
            customer_data["bank"] = Bank.objects.get(id=data.get("bank"))
        if data.get("country"):
            customer_data["country"] = Country.objects.get(id=data.get("country"))
        if data.get("city"):
            customer_data["city"] = City.objects.get(id=data.get("city"))
        if data.get("area"):
            customer_data["area"] = Area.objects.get(id=data.get("area"))  # ✅ هو ده اللي لازم يكون
        customer = Customer.objects.create(**customer_data)

        # ========== OWNER ==========
        if customer.customer_type == "owner":
            person_data = {
                k.replace("person_", ""): v for k, v in data.items() if k.startswith("person_")
            }
            person_files = {
                k.replace("person_", ""): v for k, v in files.items() if k.startswith("person_")
            }
            person_serializer = PersonSerializer(data={**person_data, **person_files})
            person_serializer.is_valid(raise_exception=True)
            person_serializer.save(customer=customer)

            # Authorized People
            index = 0
            while True:
                prefix = f"authorized_people[{index}]"
                sub_data = {
                    k.replace(f"{prefix}.", ""): v
                    for k, v in data.items()
                    if k.startswith(prefix + ".")
                }
                sub_files = {
                    k.replace(f"{prefix}.", ""): v
                    for k, v in files.items()
                    if k.startswith(prefix + ".")
                }
                if not sub_data:
                    break
                serializer = AuthorizedPersonSerializer(data={**sub_data, **sub_files})
                serializer.is_valid(raise_exception=True)
                serializer.save(customer=customer)
                index += 1

        # ========== COMPANY ==========
        elif customer.customer_type in ["commercial", "consultant"]:
            company_data = {
                k.replace("company_", ""): v for k, v in data.items() if k.startswith("company_")
            }
            company_files = {
                k.replace("company_", ""): v for k, v in files.items() if k.startswith("company_")
            }
            company_serializer = CompanySerializer(data={**company_data, **company_files})
            company_serializer.is_valid(raise_exception=True)
            company_serializer.save(customer=customer)

            legal_data = {}
            legal_files = {}

            for k, v in data.items():
                if k.startswith("legal_person_"):
                    field = k.replace("legal_person_", "")
                    if field in ["gender", "nationality", "country", "city"]:
                        legal_data[f"{field}_id"] = v
                    else:
                        legal_data[field] = v

            for k, v in files.items():
                if k.startswith("legal_person_"):
                    field = k.replace("legal_person_", "")
                    legal_files[field] = v
            legal_serializer = LegalPersonSerializer(data={**legal_data, **legal_files})
            legal_serializer.is_valid(raise_exception=True)
            legal_serializer.save(customer=customer)


        # ========== CONTACT PEOPLE ==========
        index = 0
        while True:
            prefix = f"contact_people[{index}]"
            sub_data = {
                k.replace(f"{prefix}.", ""): v
                for k, v in data.items()
                if k.startswith(prefix + ".")
            }
            sub_files = {
                k.replace(f"{prefix}.", ""): v
                for k, v in files.items()
                if k.startswith(prefix + ".")
            }
            if not sub_data:
                break
            serializer = ContactPersonSerializer(data={**sub_data, **sub_files})
            serializer.is_valid(raise_exception=True)
            serializer.save(customer=customer)
            index += 1

        return customer
    def update(self, instance, validated_data):
        request = self.context.get("request")
        data = request.data
        files = request.FILES

        # تحديث الحقول العادية
        for field in [
            "name_ar", "name_en", "email",
            "telephone_number", "whatsapp_number", "notes",
            "account_holder_name", "account_number", "iban_number"
        ]:
            setattr(instance, field, data.get(field, getattr(instance, field)))

        if data.get("iban_certificate"):
            instance.iban_certificate = data.get("iban_certificate")

        # العلاقات
        from shared.models import Bank, Country, City, Area
        if data.get("bank"):
            instance.bank = Bank.objects.get(id=data.get("bank"))
        if data.get("country"):
            instance.country = Country.objects.get(id=data.get("country"))
        if data.get("city"):
            instance.city = City.objects.get(id=data.get("city"))
        if data.get("area"):
            instance.area = Area.objects.get(id=data.get("area"))

        instance.save()

        # ========== OWNER ==========
        if instance.customer_type == "owner":
            person = getattr(instance, "person", None)
            if person:
                person_data = {
                    k.replace("person_", ""): v for k, v in data.items() if k.startswith("person_")
                }
                person_files = {
                    k.replace("person_", ""): v for k, v in files.items() if k.startswith("person_")
                }
                person_serializer = PersonSerializer(person, data={**person_data, **person_files}, partial=True)
                person_serializer.is_valid(raise_exception=True)
                person_serializer.save()

        # ========== COMPANY ==========
        elif instance.customer_type in ["commercial", "consultant"]:
            company = getattr(instance, "company", None)
            if company:
                company_data = {
                    k.replace("company_", ""): v for k, v in data.items() if k.startswith("company_")
                }
                company_files = {
                    k.replace("company_", ""): v for k, v in files.items() if k.startswith("company_")
                }
                company_serializer = CompanySerializer(company, data={**company_data, **company_files}, partial=True)
                company_serializer.is_valid(raise_exception=True)
                company_serializer.save()

            # LegalPerson
            legal = getattr(instance, "legal_person", None)
            if legal:
                legal_data = {}
                legal_files = {}
                for k, v in data.items():
                    if k.startswith("legal_person_"):
                        field = k.replace("legal_person_", "")
                        if field in ["gender", "nationality", "country", "city"]:
                            legal_data[f"{field}_id"] = v
                        else:
                            legal_data[field] = v
                for k, v in files.items():
                    if k.startswith("legal_person_"):
                        field = k.replace("legal_person_", "")
                        legal_files[field] = v
                legal_serializer = LegalPersonSerializer(legal, data={**legal_data, **legal_files}, partial=True)
                legal_serializer.is_valid(raise_exception=True)
                legal_serializer.save()
            # ========== AUTHORIZED PEOPLE ==========
        if instance.customer_type == "owner":
            # نحذف القديم (أسهل وأضمن)
            instance.authorized_people.all().delete()

            index = 0
            while True:
                prefix = f"authorized_people[{index}]"
                sub_data = {
                    k.replace(f"{prefix}.", ""): v
                    for k, v in data.items()
                    if k.startswith(prefix + ".")
                }
                sub_files = {
                    k.replace(f"{prefix}.", ""): v
                    for k, v in files.items()
                    if k.startswith(prefix + ".")
                }
                if not sub_data:
                    break
                serializer = AuthorizedPersonSerializer(data={**sub_data, **sub_files})
                serializer.is_valid(raise_exception=True)
                serializer.save(customer=instance)
                index += 1

        # ========== CONTACT PEOPLE ==========
        if instance.customer_type in ["commercial", "consultant"]:
            instance.contact_people.all().delete()

            index = 0
            while True:
                prefix = f"contact_people[{index}]"
                sub_data = {
                    k.replace(f"{prefix}.", ""): v
                    for k, v in data.items()
                    if k.startswith(prefix + ".")
                }
                sub_files = {
                    k.replace(f"{prefix}.", ""): v
                    for k, v in files.items()
                    if k.startswith(prefix + ".")
                }
                if not sub_data:
                    break
                serializer = ContactPersonSerializer(data={**sub_data, **sub_files})
                serializer.is_valid(raise_exception=True)
                serializer.save(customer=instance)
                index += 1


        return instance
