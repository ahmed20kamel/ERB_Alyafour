from django.contrib import admin
from .models import Category, Document


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'expires_on',
                    'owner_email', 'days_to_expiry')
    list_filter = ('category', 'expires_on')
    search_fields = ('title', 'owner_email')
