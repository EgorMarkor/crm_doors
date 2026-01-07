from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        OWNER = 'owner', 'Владелец'
        MANAGER = 'manager', 'Менеджер'
        INSTALLER = 'installer', 'Установщик'
        DELIVERY = 'delivery', 'Доставщик'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.MANAGER)

    def is_owner(self) -> bool:
        return self.role == self.Roles.OWNER

    def is_manager(self) -> bool:
        return self.role == self.Roles.MANAGER

    def is_installer(self) -> bool:
        return self.role == self.Roles.INSTALLER

    def is_delivery(self) -> bool:
        return self.role == self.Roles.DELIVERY


class BaseRequest(models.Model):
    client_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    scheduled_for = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_manager',
        limit_choices_to={'role': User.Roles.MANAGER},
    )

    class Meta:
        abstract = True
        ordering = ['scheduled_for']

    def __str__(self) -> str:
        return f"{self.client_name} ({self.scheduled_for:%d.%m.%Y %H:%M})"


class InstallationRequest(BaseRequest):
    installer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='installation_requests',
        limit_choices_to={'role': User.Roles.INSTALLER},
    )
    status = models.CharField(max_length=50, default='В ожидании установки')


class DeliveryRequest(BaseRequest):
    courier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_requests',
        limit_choices_to={'role': User.Roles.DELIVERY},
    )
    status = models.CharField(max_length=50, default='В ожидании доставки')
