from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from accounts.models import User,ModulePermission
from inventory.models import Product
from sales.models import Customer, Sale
from dealers.models import DealerPayment
from django.db.models import Sum
from inventory.models import DealerStock
from decimal import Decimal
from accounts.models import User
from dealers.models import (
    DealerProfile,
    DealerLedger,
    DealerPayment,
    Dealer,
    
)

from dealer_portal.models import(DealerVehicle)
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

from inventory.models import (
    Supplier,
    RawMaterial,
    Production,
    RawMaterialPurchase,
    DealerStock,
)

from django.utils import timezone





@login_required
def super_dashboard(request):

    if request.user.role != "SUPER_ADMIN":
        return redirect("login")

    # -------------------------
    # Totals
    # -------------------------

    total_sales = (
        Sale.objects.aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0")
    )

    # vehicle_sales = (
    #     VehicleDispatchSale.objects.aggregate(
    #         total=Sum("amount")
    #     )["total"]
    #     or Decimal("0")
    # )

    dealer_outstanding = (
        DealerLedger.objects.aggregate(
            total=Sum("balance")
        )["total"]
        or Decimal("0")
    )

    total_payments = (
        DealerLedger.objects.aggregate(
            total=Sum("credit")
        )["total"]
        or Decimal("0")
    )

    # -------------------------
    # Dealer Summary
    # -------------------------

    dealer_summary = []

    for dealer in Dealer.objects.all():

        # Outstanding
        outstanding = (
            DealerLedger.objects.filter(
                dealer=dealer
            ).aggregate(
                total=Sum("balance")
            )["total"]
            or Decimal("0")
        )

        # Dealer Stock Value
        stock_value = Decimal("0")

        for stock in DealerStock.objects.filter(
            dealer=dealer
        ).select_related("product"):

            rate = getattr(stock.product, "selling_price", Decimal("0"))

            stock_value += stock.quantity * rate

        dealer_summary.append({

            "dealer": dealer,

            "sales": Decimal("0"),   # can improve later

            "vehicle_sales": Decimal("0"),  # can improve later

            "outstanding": outstanding,

            "stock": stock_value,

        })

    context = {

        # Dealers

        "total_dealers":
            Dealer.objects.count(),

        "total_company_staff":
            User.objects.filter(
                role="COMPANY_STAFF"
            ).count(),

        "total_dealer_staff":
            User.objects.filter(
                role="DEALER_STAFF"
            ).count(),

        "total_vehicles":
            DealerVehicle.objects.count(),

        # Master Data

        "total_products":
            Product.objects.count(),

        "total_customers":
            Customer.objects.count(),

        "total_suppliers":
            Supplier.objects.count(),

        "total_employees":
            User.objects.count(),

        # Business

        "company_sales":
            total_sales,

        # "vehicle_sales":
        #     vehicle_sales,

        "dealer_outstanding":
            dealer_outstanding,

        "total_payments":
            total_payments,

        # Inventory

        "total_raw_materials":
            RawMaterial.objects.count(),

        "total_finished_products":
            Product.objects.count(),

        "total_production":
            Production.objects.count(),

        "total_purchases":
            RawMaterialPurchase.objects.count(),

        # Dealer Table

        "dealer_summary":
            dealer_summary,

    }

    return render(
        request,
        "dashboard/super_admin/dashboard.html",
        context,
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

from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from dealers.models import Dealer, DealerLedger
from dealer_portal.models import VehicleDispatch, VehicleDispatchSale
from sales.models import Sale



@login_required
def super_dealer_dashboard(request, pk):

    if request.user.role != "SUPER_ADMIN":
        return redirect("login")

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    # ---------------------------------
    # Dealer Stock
    # ---------------------------------

    stocks = DealerStock.objects.filter(
        dealer=dealer
    ).select_related("product")

    stock_value = Decimal("0")

    for stock in stocks:

        rate = getattr(
            stock.product,
            "selling_price",
            Decimal("0")
        )

        stock_value += stock.quantity * rate

    # ---------------------------------
    # Dealer Ledger
    # ---------------------------------

    ledgers = DealerLedger.objects.filter(
        dealer=dealer
    ).order_by("-created_at")

    debit = ledgers.aggregate(
        total=Sum("debit")
    )["total"] or Decimal("0")

    credit = ledgers.aggregate(
        total=Sum("credit")
    )["total"] or Decimal("0")

    outstanding = debit - credit

    # ---------------------------------
    # Dealer Counter Sales
    # ---------------------------------

    dealer_sales_total = DealerSale.objects.filter(
        dealer=dealer
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    # ---------------------------------
    # Vehicle Sales
    # ---------------------------------

    vehicle_sales_total = VehicleDispatchSale.objects.filter(
        dispatch__dealer=dealer
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    # ---------------------------------
    # Total Sales
    # ---------------------------------

    total_sales = dealer_sales_total + vehicle_sales_total

    # ---------------------------------
    # Vehicle Dispatches
    # ---------------------------------

    dispatches = VehicleDispatch.objects.filter(
        dealer=dealer
    ).order_by("-dispatch_date")

    context = {

        "dealer": dealer,

        "stocks": stocks,

        "stock_value": stock_value,

        "dispatches": dispatches,

        "ledgers": ledgers,

        "dealer_sales": dealer_sales_total,

        "vehicle_sales": vehicle_sales_total,

        "total_sales": total_sales,

        "outstanding": outstanding,

    }

    return render(

        request,

        "dashboard/super_admin/dealer_dashboard.html",

        context

    )


@login_required
def dealer_statement_form(request):

    if request.user.role != "SUPER_ADMIN":
        return redirect("login")

    dealers = Dealer.objects.filter(
        is_active=True
    ).order_by("name")

    return render(

        request,

        "dashboard/dealers/dealer_statement_form.html",

        {

            "dealers": dealers

        }

    )


@login_required
def super_dealer_statement(request, pk):

    if request.user.role != "SUPER_ADMIN":
        return redirect("login")

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    if request.method == "POST":

        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")

        return redirect(
            f"/dashboard/super/dealer/{dealer.id}/statement/report/?from_date={from_date}&to_date={to_date}"
        )

    return render(
        request,
        "dashboard/super_admin/dealer_statement_form.html",
        {
            "dealer": dealer
        }
    )


@login_required
def super_dealer_statement_report(request, pk):

    if request.user.role != "SUPER_ADMIN":
        return redirect("login")

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    opening = DealerLedger.objects.filter(
        dealer=dealer,
        created_at__date__lt=from_date
    )

    opening_balance = (
        opening.aggregate(
            debit=Sum("debit"),
            credit=Sum("credit")
        )["debit"] or Decimal("0")
    ) - (
        opening.aggregate(
            debit=Sum("debit"),
            credit=Sum("credit")
        )["credit"] or Decimal("0")
    )

    ledgers = DealerLedger.objects.filter(
        dealer=dealer,
        created_at__date__range=[from_date, to_date]
    ).order_by("created_at")

    running_balance = opening_balance

    statement = []

    total_debit = Decimal("0")
    total_credit = Decimal("0")

    for row in ledgers:

        running_balance += row.debit
        running_balance -= row.credit

        total_debit += row.debit
        total_credit += row.credit

        statement.append({

            "date": row.created_at,

            "reference": row.reference,

            "debit": row.debit,

            "credit": row.credit,

            "balance": running_balance,

        })

    return render(

        request,

        "dashboard/super_admin/dealer_statement.html",

        {

            "dealer": dealer,

            "statement": statement,

            "opening_balance": opening_balance,

            "closing_balance": running_balance,

            "total_debit": total_debit,

            "total_credit": total_credit,

            "from_date": from_date,

            "to_date": to_date,

        }

    )