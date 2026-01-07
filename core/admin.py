from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import DeliveryRequest, InstallationRequest, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Роль", {"fields": ("role",)}),)
    list_display = UserAdmin.list_display + ("role",)
    list_filter = UserAdmin.list_filter + ("role",)


@admin.register(InstallationRequest)
class InstallationRequestAdmin(admin.ModelAdmin):
    list_display = ("client_name", "scheduled_for", "installer", "manager", "status")
    list_filter = ("status", "installer", "manager")
    search_fields = ("client_name", "phone", "address")


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ("client_name", "scheduled_for", "courier", "manager", "status")
    list_filter = ("status", "courier", "manager")
    search_fields = ("client_name", "phone", "address")
