from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import Gender  # دي من الكور عشان تكون مرجعية موحدة

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.ForeignKey(
        Gender,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=30, blank=True, null=True)

    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('supervisor', 'Supervisor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    def __str__(self):
        return self.username
