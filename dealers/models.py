from django.db import models
from django.conf import settings




class Dealer(models.Model):

    name = models.CharField(max_length=200)

    address = models.TextField()

    phone = models.CharField(max_length=20)

    email = models.EmailField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dealers'
    )
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    

class DealerProfile(models.Model):

    dealer = models.OneToOneField(
        Dealer,
        on_delete=models.CASCADE
    )

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DEALER_ADMIN'}
    )

    def __str__(self):
        return self.dealer.name
    



class DealerPayment(models.Model):

    PAYMENT_MODES = (
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
        ('ONLINE', 'Online'),
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODES
    )

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
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
        return f"{self.dealer.name} - {self.amount}"
    

class DealerLedger(models.Model):

    ENTRY_CHOICES = (
        ('DISPATCH', 'Dispatch'),
        ('PAYMENT', 'Payment'),
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_CHOICES
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.dealer.name


class DealerReturn(models.Model):

    dealer = models.ForeignKey(
        'Dealer',
        on_delete=models.CASCADE
    )

    return_no = models.CharField(
        max_length=100,
        unique=True
    )

    return_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
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
        return self.return_no
    

class DealerReturnItem(models.Model):

    dealer_return = models.ForeignKey(
        DealerReturn,
        on_delete=models.CASCADE,
        related_name='items'
        )

    product = models.ForeignKey(
        'inventory.Product',
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