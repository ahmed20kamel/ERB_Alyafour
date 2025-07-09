from django.contrib import admin
from .models import DeleteClientRequest, UpdateRequest

@admin.register(DeleteClientRequest)
class DeleteClientRequest(admin.ModelAdmin):
    list_display = ("target", "status", "requested_by", "approved_by", "created_at")

@admin.register(UpdateRequest)
class UpdateRequestAdmin(admin.ModelAdmin):
    list_display = ("target", "status", "requested_by", "approved_by", "created_at")
