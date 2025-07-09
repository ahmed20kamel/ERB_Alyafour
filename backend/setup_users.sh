#!/bin/bash

echo "🚀 Clearing old users & groups..."

# احذف كل الجروبات
echo "🗑️ Deleting old groups..."
python manage.py shell << EOF
from django.contrib.auth.models import Group, User
Group.objects.all().delete()
User.objects.all().delete()
EOF

echo "✅ Old users & groups deleted."

# كريت الجروبات
echo "🔧 Creating groups..."
python manage.py shell << EOF
from django.contrib.auth.models import Group

Group.objects.create(name="SuperAdmin")
Group.objects.create(name="Manager")
Group.objects.create(name="Employee")
Group.objects.create(name="Supervisor")
EOF

echo "✅ Groups created."

# كريت اليوزرز
echo "👤 Creating users..."
python manage.py shell << EOF
from django.contrib.auth.models import User, Group

superadmin = User.objects.create_superuser(username="superadmin", email="superadmin@alyafour.com", password="superadmin123")
manager = User.objects.create_user(username="manager", email="manager@alyafour.com", password="manager123", is_staff=True)
employee = User.objects.create_user(username="employee", email="employee@alyafour.com", password="employee123", is_staff=True)
supervisor = User.objects.create_user(username="supervisor", email="supervisor@alyafour.com", password="supervisor123", is_staff=True)

# اربطهم بالجروبات
superadmin.groups.add(Group.objects.get(name="SuperAdmin"))
manager.groups.add(Group.objects.get(name="Manager"))
employee.groups.add(Group.objects.get(name="Employee"))
supervisor.groups.add(Group.objects.get(name="Supervisor"))
EOF

echo "✅ All done. Users & groups are ready!"

