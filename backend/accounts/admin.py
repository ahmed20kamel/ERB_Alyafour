from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": (
                "profile_picture", "phone_number", "job_title", "bio",
                "gender", "date_of_birth", "address", "department", "national_id", "role"
            )
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
