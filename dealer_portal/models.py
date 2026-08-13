from django.db import models
from dealers.models import Dealer
from inventory.models import Product

class DealerCustomer(models.Model):

    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)   # ADD THIS

    address = models.TextField(blank=True, null=True)

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)   # ADD THIS

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class DealerSale(models.Model):

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    customer = models.ForeignKey(
    DealerCustomer,
    on_delete=models.CASCADE,
    related_name='sales'
    
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


class DealerSaleItem(models.Model):

    sale = models.ForeignKey(
        DealerSale,
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


class DealerCustomerPayment(models.Model):

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    customer = models.ForeignKey(
        DealerCustomer,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_date = models.DateField()



class DealerCustomerLedger(models.Model):

    customer = models.ForeignKey(
        DealerCustomer,
        on_delete=models.CASCADE
    )

    entry_type = models.CharField(
        max_length=20
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


class DealerSalesReturn(models.Model):

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    sale = models.ForeignKey(
        DealerSale,
        on_delete=models.CASCADE
    )

    return_no = models.CharField(
        max_length=100,
        unique=True
    )

    return_date = models.DateField()

    total_return_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.return_no
    




class DealerSalesReturnItem(models.Model):

    sales_return = models.ForeignKey(
        DealerSalesReturn,
        on_delete=models.CASCADE,
        related_name='items'
    )

    sale_item = models.ForeignKey(
        DealerSaleItem,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    return_qty = models.DecimalField(
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








class DealerVehicle(models.Model):

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    vehicle_no = models.CharField(
        max_length=100
    )

    driver_name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.vehicle_no
    

class VehicleDispatch(models.Model):

    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    vehicle = models.ForeignKey(
        DealerVehicle,
        on_delete=models.CASCADE
    )

    dispatch_no = models.CharField(
        max_length=100,
        unique=True
    )

    dispatch_date = models.DateField()

    dispatch_time = models.TimeField(
        blank=True,
        null=True
    )

    driver_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    return_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.dispatch_no
    

class VehicleTrip(models.Model):

    dispatch = models.ForeignKey(
        VehicleDispatch,
        on_delete=models.CASCADE,
        related_name='trips'
    )
    is_closed = models.BooleanField(default=False)

    trip_no = models.PositiveIntegerField()

    dispatch_time = models.DateTimeField(
        auto_now_add=True
    )

    remarks = models.CharField(
        max_length=300,
        blank=True
    )

    class Meta:
        ordering = ['trip_no']
        unique_together = (
            'dispatch',
            'trip_no'
        )

    def __str__(self):
        return f"{self.dispatch.dispatch_no} - Trip {self.trip_no}"

class VehicleTripItem(models.Model):

    trip = models.ForeignKey(
        VehicleTrip,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    dispatch_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    sold_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    return_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    breakage_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    leakage_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    sponsor_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    sales_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )



class VehicleDispatchSale(models.Model):

    dispatch = models.ForeignKey(
        VehicleDispatch,
        on_delete=models.CASCADE,
        related_name="sales"
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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"




class DealerSponsor(models.Model):

    SOURCE_CHOICES = (
        ('DEALER', 'Dealer'),
        ('VEHICLE', 'Vehicle'),
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE
    )

    vehicle = models.ForeignKey(
        DealerVehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    vehicle_dispatch = models.ForeignKey(
        VehicleDispatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    customer = models.ForeignKey(
        DealerCustomer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    sponsor_date = models.DateField()

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )

    remarks = models.CharField(
        max_length=300,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"