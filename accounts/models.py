from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('COMPANY_STAFF', 'Company Staff'),
        ('DEALER_ADMIN', 'Dealer Admin'),
        ('DEALER_STAFF', 'Dealer Staff'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    is_active_user = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.username
    

class ModulePermission(models.Model):

    MODULES = (
        ('DEALER', 'Dealer'),
        ('PRODUCT', 'Product'),
        ('STOCK', 'Stock'),
        ('DISPATCH', 'Dispatch'),
        ('SALES', 'Sales'),
        ('PAYMENT', 'Payment'),
        ('REPORT', 'Report'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    module = models.CharField(
        max_length=50,
        choices=MODULES
    )

    can_view = models.BooleanField(default=False)

    can_add = models.BooleanField(default=False)

    can_edit = models.BooleanField(default=False)

    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            'user',
            'module'
        )