from django.db import models
from inventory.models import Product
from django.conf import settings



class Customer(models.Model):

    name = models.CharField(max_length=200)

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

    opening_balance = models.DecimalField(
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
    

class Sale(models.Model):

    STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    invoice_no = models.CharField(
        max_length=100,
        unique=True
    )

    sale_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UNPAID'
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
        return self.invoice_no

class SaleItem(models.Model):

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
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
        return self.product.name
    

class CustomerLedger(models.Model):

    ENTRY_TYPES = (
        ('SALE', 'Sale'),
        ('PAYMENT', 'Payment'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPES
    )

    debit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

class CustomerLedger(models.Model):

    ENTRY_TYPES = (
        ('SALE', 'Sale'),
        ('PAYMENT', 'Payment'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPES
    )

    debit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class CustomerPayment(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

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
        return self.customer.name