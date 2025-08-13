from customers.serializers import CustomerSerializer

def dump_fields():
    serializer = CustomerSerializer()
    fields = list(serializer.fields.keys())
    for field in fields:
        print(field)

dump_fields()
