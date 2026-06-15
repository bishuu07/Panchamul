from django.db import models
from django.conf import settings
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from dealers.models import Dealer
from django.shortcuts import render




class RawMaterial(models.Model):

    UNIT_CHOICES = (
        ('PCS', 'Pieces'),
        ('KG', 'Kilogram'),
        ('ROLL', 'Roll'),
        ('LTR', 'Liter'),
    )

    name = models.CharField(
        max_length=200
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES
    )

    current_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    
# class RawMaterialPurchase(models.Model):

#     material = models.ForeignKey(
#         RawMaterial,
#         on_delete=models.CASCADE
#     )

#     quantity = models.DecimalField(
#         max_digits=12,
#         decimal_places=2
#     )

#     purchase_date = models.DateField()

#     remarks = models.TextField(
#         blank=True,
#         null=True
#     )

#     created_by = models.ForeignKey(
#         'accounts.User',
#         on_delete=models.SET_NULL,
#         null=True
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     def save(self, *args, **kwargs):

#         is_new = self.pk is None

#         super().save(*args, **kwargs)

#         if is_new:

#             self.material.current_stock += self.quantity

#             self.material.save()

class ProductionIssue(models.Model):

    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    issue_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    issued_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.material.current_stock -= self.quantity

            self.material.save()


class ProductionReturn(models.Model):

    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    return_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.material.current_stock += self.quantity

            self.material.save()

class Supplier(models.Model):

    name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class RawMaterialPurchase(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE
    )

    invoice_number = models.CharField(
        max_length=100
    )

    purchase_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.invoice_number
    

class RawMaterialPurchaseItem(models.Model):

    purchase = models.ForeignKey(
        RawMaterialPurchase,
        on_delete=models.CASCADE,
        related_name='items'
    )

    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return self.raw_material.name

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.raw_material.current_stock += self.quantity


            self.raw_material.save()

class MaterialIssue(models.Model):

    issue_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    issued_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Issue #{self.id}"
    

class MaterialIssueItem(models.Model):

    issue = models.ForeignKey(
        MaterialIssue,
        on_delete=models.CASCADE,
        related_name='items'
    )

    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.raw_material.current_stock -= self.quantity

            self.raw_material.save()

    def __str__(self):
        return self.raw_material.name
    

class MaterialReturn(models.Model):

    return_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Return #{self.id}"
    

class MaterialReturnItem(models.Model):

    material_return = models.ForeignKey(
        MaterialReturn,
        on_delete=models.CASCADE,
        related_name='items'
    )

    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return self.raw_material.name

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.raw_material.current_stock += self.quantity

            self.raw_material.save()


class Product(models.Model):

    UNIT_CHOICES = (
        ('PCS', 'Pieces'),
        ('BOX', 'Box'),
        ('LTR', 'Liter'),
    )

    name = models.CharField(
        max_length=200
    )

   

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES
    )

    current_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    

  

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    
class Production(models.Model):

    batch_number = models.CharField(
        max_length=100
    )

    production_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.batch_number
    

class ProductionItem(models.Model):

    production = models.ForeignKey(
        Production,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity_produced = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    quantity_wasted = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.product.name

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.product.current_stock += self.quantity_produced

            self.product.save()





class DealerStock(models.Model):

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = (
            'dealer',
            'product'
        )

    def __str__(self):

        return f"{self.dealer.name} - {self.product.name}"
    

class Dispatch(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PARTIAL', 'Partially Received'),
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    dispatch_no = models.CharField(
        max_length=100,
        unique=True
    )

    dispatch_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.dispatch_no
    

class DispatchItem(models.Model):

    dispatch = models.ForeignKey(
        Dispatch,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    dispatched_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    received_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    damaged_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    returned_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.product.name
    

class StockLedger(models.Model):

    TRANSACTION_TYPES = (
        ('PURCHASE', 'Purchase'),
        ('ISSUE', 'Issue'),
        ('RETURN', 'Return'),
        ('PRODUCTION', 'Production'),
        ('DISPATCH', 'Dispatch'),
        ('SALE', 'Sale'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.transaction_type}"