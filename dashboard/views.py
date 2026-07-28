from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from accounts.models import User,ModulePermission
from inventory.models import Product
from sales.models import Customer, Sale
from dealers.models import DealerPayment
from django.db.models import Sum
from inventory.models import DealerStock
from decimal import Decimal
from dealers.models import (
    DealerProfile,
    DealerLedger,
    DealerPayment,
    DealerReturn,
    Dealer,
)
from dealer_portal.models import (
    DealerSale,
    DealerSalesReturn,
    DealerCustomerPayment,
    DealerVehicle,
    VehicleDispatch,
    VehicleTripItem,
    DealerSponsor,
    DealerCustomer,
)
from django.utils import timezone




@login_required
def super_dashboard(request):

    if request.user.role != 'SUPER_ADMIN':
        return redirect('login')

    total_outstanding = DealerLedger.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0

    total_sales = Sale.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    context = {

        'total_dealers':
            Dealer.objects.count(),

        'total_dealer_admins':
            User.objects.filter(
                role='DEALER_ADMIN'
            ).count(),

        'total_staff':
            User.objects.filter(
                role='COMPANY_STAFF'
            ).count(),

        'total_products':
            Product.objects.count(),

        'total_customers':
            Customer.objects.count(),

        'total_sales':
            total_sales,

        'dealer_outstanding':
            total_outstanding,
    }

    return render(
        request,
        'dashboard/super_admin/dashboard.html',
        context
    )

# @login_required
# def dealer_dashboard(request):

#     try:

#         profile = DealerProfile.objects.get(
#             admin_user=request.user
#         )

#         dealer = profile.dealer

#     except DealerProfile.DoesNotExist:

#         return redirect('login')

#     outstanding = DealerLedger.objects.filter(
#         dealer=dealer
#     ).order_by('-id').first()

#     current_balance = (
#         outstanding.balance
#         if outstanding
#         else Decimal('0')
#     )

#     total_payments = DealerPayment.objects.filter(
#         dealer=dealer
#     ).aggregate(
#         total=Sum('amount')
#     )['total'] or Decimal('0')

#     total_returns = DealerReturn.objects.filter(
#         dealer=dealer
#     ).aggregate(
#         total=Sum('total_amount')
#     )['total'] or Decimal('0')

#     total_stock_items = DealerStock.objects.filter(
#         dealer=dealer
#     ).count()

#     context = {

#         'dealer': dealer,

#         'current_balance':
#             current_balance,

#         'total_payments':
#             total_payments,

#         'total_returns':
#             total_returns,

#         'total_stock_items':
#             total_stock_items,
#     }

#     return render(
#         request,
#         'dashboard/dealer/dashboard.html',
#         context
#     )

@login_required
def dealer_dashboard(request):

    try:
        profile = DealerProfile.objects.get(
            admin_user=request.user
        )

        dealer = profile.dealer

    except DealerProfile.DoesNotExist:
        return redirect('login')

    today = timezone.localdate()

    # -----------------------------------
    # Outstanding Amount
    # -----------------------------------

    current_balance = (
        DealerSale.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('due_amount')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Today's Sales
    # -----------------------------------

    today_sales = (
        DealerSale.objects.filter(
            dealer=dealer,
            sale_date=today
        ).aggregate(
            total=Sum('total_amount')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Monthly Sales
    # -----------------------------------

    month_sales = (
        DealerSale.objects.filter(
            dealer=dealer,
            sale_date__year=today.year,
            sale_date__month=today.month
        ).aggregate(
            total=Sum('total_amount')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Total Payments
    # -----------------------------------

    total_payments = (
        DealerCustomerPayment.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('amount')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Sales Returns
    # -----------------------------------

    total_returns = (
        DealerSalesReturn.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('total_return_amount')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Products
    # -----------------------------------

    total_products = DealerStock.objects.filter(
        dealer=dealer
    ).count()

    # -----------------------------------
    # Total Stock
    # -----------------------------------

    total_stock_qty = (
        DealerStock.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('quantity')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Vehicles
    # -----------------------------------

    total_vehicles = DealerVehicle.objects.filter(
        dealer=dealer
    ).count()

    # -----------------------------------
    # Open Dispatch
    # -----------------------------------

    open_dispatches = VehicleDispatch.objects.filter(
        dealer=dealer,
        status='OPEN'
    ).count()

    # -----------------------------------
    # Sponsor Quantity
    # -----------------------------------

    sponsor_qty = (
        DealerSponsor.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('quantity')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Breakage Quantity
    # -----------------------------------

    breakage_qty = (
        VehicleTripItem.objects.filter(
            trip__dispatch__dealer=dealer
        ).aggregate(
            total=Sum('breakage_qty')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Leakage Quantity
    # -----------------------------------

    leakage_qty = (
        VehicleTripItem.objects.filter(
            trip__dispatch__dealer=dealer
        ).aggregate(
            total=Sum('leakage_qty')
        )['total']
        or Decimal('0')
    )

    # -----------------------------------
    # Recent Sales
    # -----------------------------------

    recent_sales = (
        DealerSale.objects.filter(
            dealer=dealer
        )
        .select_related('customer')
        .order_by('-sale_date', '-id')[:10]
    )

    # -----------------------------------
    # Low Stock
    # -----------------------------------

    low_stock = (
        DealerStock.objects.filter(
            dealer=dealer,
            quantity__lte=10
        )
        .select_related('product')
        .order_by('quantity')
    )

    # -----------------------------------
    # Top Outstanding Customers
    # -----------------------------------

    top_due_customers = (
        DealerCustomer.objects.filter(
            dealer=dealer
        )
        .annotate(
            total_due=Sum('sales__due_amount')
        )
        .order_by('-total_due')[:5]
    )

    context = {

        'dealer': dealer,

        'current_balance': current_balance,

        'today_sales': today_sales,

        'month_sales': month_sales,

        'total_payments': total_payments,

        'total_returns': total_returns,

        'total_products': total_products,

        'total_stock_qty': total_stock_qty,

        'total_vehicles': total_vehicles,

        'open_dispatches': open_dispatches,

        'sponsor_qty': sponsor_qty,

        'breakage_qty': breakage_qty,

        'leakage_qty': leakage_qty,

        'recent_sales': recent_sales,

        'low_stock': low_stock,

        'top_due_customers': top_due_customers,
    }

    return render(
        request,
        'dashboard/dealer/dashboard.html',
        context
    )



@login_required
def staff_dashboard(request):

    permissions = ModulePermission.objects.filter(
        user=request.user,
        can_view=True
    )

    context = {
        'permissions': permissions,
        'total_products': Product.objects.count(),
        'total_sales': Sale.objects.count(),
    }

    return render(
        request,
        'dashboard/staff/dashboard.html',
        context
    )

@login_required
def dealer_staff_dashboard(request):

    return render(
        request,
        'dashboard/dealer_staff/dashboard.html'
    )

