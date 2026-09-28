from django.conf import settings
from django.db import models


class CompanyExpense(models.Model):

    CATEGORY_CHOICES = (
        ("VEHICLE_FUEL", "Vehicle Fuel"),
        ("VEHICLE_REPAIR", "Vehicle Repair"),
        ("VEHICLE_MAINTENANCE", "Vehicle Maintenance"),
        ("OFFICE", "Office Expense"),
        ("SALARY", "Salary / Allowance"),
        ("TRANSPORT", "Transport"),
        ("LOADING", "Loading / Unloading"),
        ("OTHER", "Other"),
    )

    expense_date = models.DateField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    vehicle = models.ForeignKey(
        "dealer_portal.DealerVehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="company_expenses_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.expense_date} - {self.amount}"


class DealerExpense(models.Model):

    CATEGORY_CHOICES = (
        ("SHOP", "Shop Expense"),
        ("STAFF", "Staff Expense"),
        ("VEHICLE_FUEL", "Vehicle Fuel"),
        ("VEHICLE_REPAIR", "Vehicle Repair"),
        ("VEHICLE_MAINTENANCE", "Vehicle Maintenance"),
        ("ELECTRICITY", "Electricity"),
        ("RENT", "Rent"),
        ("TRANSPORT", "Transport"),
        ("OTHER", "Other"),
    )

    dealer = models.ForeignKey(
        "dealers.Dealer",
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    expense_date = models.DateField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dealer_expenses_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.dealer.name} - {self.amount}"


class TripExpense(models.Model):

    CATEGORY_CHOICES = (
        ("FUEL", "Fuel"),
        ("FOOD", "Food / Snacks"),
        ("PARKING", "Parking"),
        ("DRIVER", "Driver Expense"),
        ("LOADING", "Loading / Unloading"),
        ("REPAIR", "Emergency Repair"),
        ("TOLL", "Toll / Road Expense"),
        ("OTHER", "Other"),
    )

    trip = models.ForeignKey(
        "dealer_portal.VehicleTrip",
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    expense_date = models.DateField(
        auto_now_add=True
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="trip_expenses_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.trip} - "
            f"{self.category} - "
            f"{self.amount}"
        )