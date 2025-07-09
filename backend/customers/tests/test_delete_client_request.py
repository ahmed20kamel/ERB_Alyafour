import pytest
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from customers.models import Customer, DeleteClientRequest


@pytest.mark.django_db
def test_employee_can_request_delete_and_manager_can_approve():
    # create groups
    employee_group = Group.objects.create(name="Employee")
    manager_group = Group.objects.create(name="Manager")

    # create users
    employee = User.objects.create_user(username="emp", password="pass")
    manager = User.objects.create_user(username="mgr", password="pass")

    employee.groups.add(employee_group)
    manager.groups.add(manager_group)

    # create customer
    customer = Customer.objects.create(
        customer_type="owner",
        full_name_arabic="عميل",
        full_name_english="Client",
        email="c@example.com",
        telephone_number="123456",
        whatsapp_number="123456",
        bank_account="12345"
    )

    # employee requests delete
    client = APIClient()
    client.login(username="emp", password="pass")

    response = client.post("/api/delete-requests/", {"customer": customer.id})
    assert response.status_code == 201
    assert DeleteClientRequest.objects.filter(customer=customer).exists()
    delete_request = DeleteClientRequest.objects.get(customer=customer)
    assert delete_request.status == "pending"

    # manager approves
    client.logout()
    client.login(username="mgr", password="pass")
    response = client.post(f"/api/delete-requests/{delete_request.id}/approve/")
    assert response.status_code == 200

    delete_request.refresh_from_db()
    assert delete_request.status == "approved"
    customer.refresh_from_db()
    assert customer.deleted_at is not None

@pytest.mark.django_db
def test_manager_can_reject_delete_request():
    # create groups
    employee_group = Group.objects.create(name="Employee")
    manager_group = Group.objects.create(name="Manager")

    # create users
    employee = User.objects.create_user(username="emp2", password="pass")
    manager = User.objects.create_user(username="mgr2", password="pass")

    employee.groups.add(employee_group)
    manager.groups.add(manager_group)

    # create customer
    customer = Customer.objects.create(
        customer_type="owner",
        full_name_arabic="عميل",
        full_name_english="Client2",
        email="c2@example.com",
        telephone_number="123456",
        whatsapp_number="123456",
        bank_account="12345"
    )

    # employee requests delete
    client = APIClient()
    client.login(username="emp2", password="pass")
    response = client.post("/api/delete-requests/", {"customer": customer.id})
    delete_request = DeleteClientRequest.objects.get(customer=customer)

    # manager rejects
    client.logout()
    client.login(username="mgr2", password="pass")
    response = client.post(f"/api/delete-requests/{delete_request.id}/reject/", {"comment": "مش مقتنع"})
    assert response.status_code == 200

    delete_request.refresh_from_db()
    assert delete_request.status == "rejected"
    assert delete_request.comment == "مش مقتنع"

@pytest.mark.django_db
def test_employee_cannot_approve():
    employee_group = Group.objects.create(name="Employee")
    employee = User.objects.create_user(username="emp3", password="pass")
    employee.groups.add(employee_group)

    customer = Customer.objects.create(
        customer_type="owner",
        full_name_arabic="عميل",
        full_name_english="Client3",
        email="c3@example.com",
        telephone_number="123456",
        whatsapp_number="123456",
        bank_account="12345"
    )

    delete_request = DeleteClientRequest.objects.create(
        customer=customer,
        requested_by=employee
    )

    client = APIClient()
    client.login(username="emp3", password="pass")
    response = client.post(f"/api/delete-requests/{delete_request.id}/approve/")
    assert response.status_code == 403
