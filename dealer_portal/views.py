
from django.contrib.auth.decorators import login_required
from .models import DealerCustomer, DealerSalesReturn, DealerSalesReturnItem
from django.shortcuts import render, redirect,get_object_or_404
from dealers.models import DealerProfile
from inventory.models import DealerStock
from .forms import DealerCustomerForm,DealerSaleForm, DealerVehicleForm,DealerSponsorForm
from dealers.models import DealerProfile
from inventory.models import Dispatch, DispatchItem,Product,DealerStock
from decimal import Decimal
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from datetime import date
from .utils import add_customer_ledger

from .models import (
    DealerSale,
    DealerSaleItem,
    DealerCustomerLedger,
    DealerCustomerPayment,
    DealerVehicle,
    DealerVehicle,
    VehicleDispatch,
    VehicleTripItem,
    DealerSponsor,
    VehicleTrip,
    VehicleDispatchSale,
    
)







@login_required
def dealer_home(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dealer = profile.dealer

    today = timezone.localdate()

    # -----------------------------
    # Today's Sales
    # -----------------------------
    today_sales = (
        DealerSale.objects.filter(
            dealer=dealer,
            sale_date=today
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Monthly Sales
    # -----------------------------
    month_sales = (
        DealerSale.objects.filter(
            dealer=dealer,
            sale_date__year=today.year,
            sale_date__month=today.month
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Payments
    # -----------------------------
    total_payments = (
        DealerCustomerPayment.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Outstanding
    # -----------------------------
    current_balance = (
        DealerSale.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('due_amount')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Returns
    # -----------------------------
    total_returns = (
        DealerSalesReturn.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('total_return_amount')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Products
    # -----------------------------
    total_products = DealerStock.objects.filter(
        dealer=dealer
    ).count()

    # -----------------------------
    # Stock Quantity
    # -----------------------------
    total_stock_qty = (
        DealerStock.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('quantity')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Vehicles
    # -----------------------------
    total_vehicles = DealerVehicle.objects.filter(
        dealer=dealer
    ).count()

    # -----------------------------
    # Open Dispatches
    # -----------------------------
    open_dispatches = VehicleDispatch.objects.filter(
        dealer=dealer,
        status='OPEN'
    ).count()

    # -----------------------------
    # Sponsor Qty
    # -----------------------------
    sponsor_qty = (
        DealerSponsor.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('quantity')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Breakage Qty
    # -----------------------------
    breakage_qty = (
        VehicleTripItem.objects.filter(
            dispatch__dealer=dealer
        ).aggregate(
            total=Sum('breakage_qty')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Leakage Qty
    # -----------------------------
    leakage_qty = (
        VehicleTripItem.objects.filter(
            dispatch__dealer=dealer
        ).aggregate(
            total=Sum('leakage_qty')
        )['total'] or Decimal('0')
    )

    # -----------------------------
    # Recent Sales
    # -----------------------------
    recent_sales = DealerSale.objects.filter(
        dealer=dealer
    ).select_related(
        'customer'
    ).order_by(
        '-id'
    )[:10]

    # -----------------------------
    # Low Stock
    # -----------------------------
    low_stock = DealerStock.objects.filter(
        dealer=dealer,
        quantity__lte=10
    ).select_related(
        'product'
    )

    # -----------------------------
    # Top Outstanding Customers
    # -----------------------------
    top_due_customers = (
        DealerCustomer.objects.filter(
            dealer=dealer
        )
        .annotate(
            total_due=Sum('dealersale__due_amount')
        )
        .order_by('-total_due')[:5]
    )

    return render(
        request,
        'dashboard/dealer/dashboard.html',
        {
            'dealer': dealer,

            'today_sales': today_sales,
            'month_sales': month_sales,

            'current_balance': current_balance,
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
    )


# from django.http import HttpResponse
# @login_required
# def dealer_home(request):

#     return HttpResponse("THIS IS MY DEALER HOME")



@login_required
def dealer_stock_list(request):

    try:
        profile = DealerProfile.objects.get(
            admin_user=request.user
        )

        dealer = profile.dealer

    except DealerProfile.DoesNotExist:
        return redirect('login')

    stocks = DealerStock.objects.filter(
        dealer=dealer
    ).select_related(
        'product'
    ).order_by(
        'product__name'
    )

    return render(
        request,
        'dealer_portal/dealer_stock_list.html',
        {
            'stocks': stocks
        }
    )


@login_required
def dealer_customer_list(request):

    try:
        profile = DealerProfile.objects.get(
            admin_user=request.user
        )
        dealer = profile.dealer

    except DealerProfile.DoesNotExist:
        return redirect('login')

    customers = DealerCustomer.objects.filter(
        dealer=dealer
    ).order_by('-id')

    return render(
        request,
        'dealer_portal/customer_list.html',
        {
            'customers': customers
        }
    )


@login_required
def dealer_customer_create(request):

    try:
        profile = DealerProfile.objects.get(
            admin_user=request.user
        )
        dealer = profile.dealer

    except DealerProfile.DoesNotExist:
        return redirect('login')

    form = DealerCustomerForm(
        request.POST or None
    )

    if form.is_valid():

        customer = form.save(commit=False)
        customer.dealer = dealer
        customer.save()

        return redirect('dealer_customer_list')

    return render(
        request,
        'dealer_portal/customer_create.html',
        {
            'form': form
        }
    )

from django.utils import timezone
from inventory.models import Dispatch
from dealers.models import DealerProfile



@login_required
def dealer_pending_dispatch_list(request):

    profile = DealerProfile.objects.get(admin_user=request.user)
    dealer = profile.dealer

    dispatches = Dispatch.objects.filter(
        dealer=dealer,
        status='PENDING'
    ).order_by('-id')

    return render(
        request,
        'dealer_portal/dispatch_list.html',
        {'dispatches': dispatches}
    )

# @login_required
# def dealer_dispatch_approve(request, pk):

#     profile = DealerProfile.objects.get(admin_user=request.user)
#     dealer = profile.dealer

#     dispatch = get_object_or_404(
#         Dispatch,
#         pk=pk,
#         dealer=dealer,
#         status='PENDING'
#     )

#     if request.method == 'POST':

#         # Mark approved
#         dispatch.status = 'APPROVED'
#         dispatch.dealer_approved_by = request.user
#         dispatch.approved_at = timezone.now()
#         dispatch.save()

#         # CREATE DEALER STOCK
#         for item in dispatch.items.all():

#             DealerStock.objects.create(
#                 dealer=dealer,
#                 product=item.product,
#                 quantity=item.dispatched_qty
#             )

#         return redirect('dealer_pending_dispatch_list')

#     return render(
#         request,
#         'dealer_portal/dispatch_approval.html',
#         {'dispatch': dispatch}
#     )


@login_required
def dealer_dispatch_approve(request, pk):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    dispatch = get_object_or_404(
        Dispatch,
        pk=pk,
        dealer=dealer
    )

    # Do not allow already approved dispatch to come through
    # the approval page.
    if dispatch.status != 'PENDING':

        return redirect(
            'dealer_dispatch_edit',
            dispatch.id
        )

    items = dispatch.items.select_related(
        'product'
    ).all()

    if request.method == 'POST':

        total_dispatched = Decimal('0')
        total_received = Decimal('0')
        total_damaged = Decimal('0')
        total_returned = Decimal('0')

        errors = []

        for item in items:

            received_qty = Decimal(
                request.POST.get(
                    f'received_{item.id}',
                    '0'
                ) or '0'
            )

            damaged_qty = Decimal(
                request.POST.get(
                    f'damaged_{item.id}',
                    '0'
                ) or '0'
            )

            returned_qty = Decimal(
                request.POST.get(
                    f'returned_{item.id}',
                    '0'
                ) or '0'
            )

            # Prevent negative quantities
            if (
                received_qty < 0
                or damaged_qty < 0
                or returned_qty < 0
            ):
                errors.append(
                    f'{item.product.name}: quantities cannot be negative.'
                )
                continue

            item_total = (
                received_qty
                + damaged_qty
                + returned_qty
            )

            # IMPORTANT:
            # received + damaged + returned
            # must exactly equal dispatched quantity.
            if item_total != item.dispatched_qty:

                errors.append(
                    f'{item.product.name}: '
                    f'Dispatched {item.dispatched_qty}, '
                    f'but Received + Damaged + Returned = '
                    f'{item_total}.'
                )

                continue

            total_dispatched += item.dispatched_qty
            total_received += received_qty
            total_damaged += damaged_qty
            total_returned += returned_qty

            item.received_qty = received_qty
            item.damaged_qty = damaged_qty
            item.returned_qty = returned_qty

            item.save(
                update_fields=[
                    'received_qty',
                    'damaged_qty',
                    'returned_qty'
                ]
            )

        # If validation failed, do not approve.
        if errors:

            return render(
                request,
                'dealer_portal/dispatch_approval.html',
                {
                    'dispatch': dispatch,
                    'items': items,
                    'errors': errors,
                }
            )

        # Safety check
        if total_dispatched <= 0:

            return render(
                request,
                'dealer_portal/dispatch_approval.html',
                {
                    'dispatch': dispatch,
                    'items': items,
                    'errors': [
                        'Dispatch has no valid quantity.'
                    ],
                }
            )

        # Since every item must completely match,
        # the dispatch is APPROVED.
        dispatch.status = 'APPROVED'
        dispatch.dealer_approved_by = request.user
        dispatch.approved_at = timezone.now()

        dispatch.save(
            update_fields=[
                'status',
                'dealer_approved_by',
                'approved_at'
            ]
        )

        return redirect(
            'dealer_dispatch_list'
        )

    return render(
        request,
        'dealer_portal/dispatch_approval.html',
        {
            'dispatch': dispatch,
            'items': items,
        }
    )


@login_required
def dealer_dispatch_edit(request, pk):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    dispatch = get_object_or_404(
        Dispatch,
        pk=pk,
        dealer=dealer
    )

    # Only approved/partial dispatches can be edited.
    if dispatch.status not in ['APPROVED', 'PARTIAL']:

        return redirect(
            'dealer_dispatch_approval',
            dispatch.id
        )

    items = list(
        dispatch.items.select_related(
            'product'
        ).all()
    )

    if request.method == 'POST':

        errors = []

        # Store old received quantities first.
        old_received = {}

        for item in items:

            old_received[item.id] = (
                item.received_qty or Decimal('0')
            )

        # -----------------------------------
        # Validate everything FIRST
        # -----------------------------------

        new_values = {}

        for item in items:

            received_qty = Decimal(
                request.POST.get(
                    f'received_{item.id}',
                    '0'
                ) or '0'
            )

            damaged_qty = Decimal(
                request.POST.get(
                    f'damaged_{item.id}',
                    '0'
                ) or '0'
            )

            returned_qty = Decimal(
                request.POST.get(
                    f'returned_{item.id}',
                    '0'
                ) or '0'
            )

            if (
                received_qty < 0
                or damaged_qty < 0
                or returned_qty < 0
            ):

                errors.append(
                    f'{item.product.name}: '
                    'quantities cannot be negative.'
                )

                continue

            total = (
                received_qty
                + damaged_qty
                + returned_qty
            )

            if total != item.dispatched_qty:

                errors.append(
                    f'{item.product.name}: '
                    f'Dispatched {item.dispatched_qty}, '
                    f'but Received + Damaged + Returned = '
                    f'{total}.'
                )

                continue

            new_values[item.id] = {
                'received': received_qty,
                'damaged': damaged_qty,
                'returned': returned_qty,
            }

        # Don't modify database if anything is invalid.
        if errors:

            return render(
                request,
                'dealer_portal/dispatch_approval.html',
                {
                    'dispatch': dispatch,
                    'items': items,
                    'errors': errors,
                    'edit_mode': True,
                }
            )

        # -----------------------------------
        # Update stock + dispatch items
        # -----------------------------------

        for item in items:

            values = new_values[item.id]

            new_received = values['received']

            old_qty = old_received[item.id]

            # Difference in received stock
            stock_difference = (
                new_received - old_qty
            )

            if stock_difference != 0:

                stock, created = DealerStock.objects.get_or_create(
                    dealer=dealer,
                    product=item.product,
                    defaults={
                        'quantity': Decimal('0')
                    }
                )

                current_stock = (
                    stock.quantity
                    or Decimal('0')
                )

                new_stock = (
                    current_stock
                    + stock_difference
                )

                # Never allow negative stock
                if new_stock < 0:

                    errors.append(
                        f'{item.product.name}: '
                        'stock cannot become negative.'
                    )

                    continue

                stock.quantity = new_stock
                stock.save(
                    update_fields=['quantity']
                )

            # Update dispatch item
            item.received_qty = values['received']
            item.damaged_qty = values['damaged']
            item.returned_qty = values['returned']

            item.save(
                update_fields=[
                    'received_qty',
                    'damaged_qty',
                    'returned_qty'
                ]
            )

        if errors:

            return render(
                request,
                'dealer_portal/dispatch_approval.html',
                {
                    'dispatch': dispatch,
                    'items': items,
                    'errors': errors,
                    'edit_mode': True,
                }
            )

        return redirect(
            'dealer_dispatch_list'
        )

    return render(
        request,
        'dealer_portal/dispatch_approval.html',
        {
            'dispatch': dispatch,
            'items': items,
            'edit_mode': True,
        }
    )

@login_required
def dealer_dispatch_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dispatches = Dispatch.objects.filter(
        dealer=profile.dealer
    ).order_by(
        '-id'
    )

    return render(
        request,
        'dealer_portal/dispatch_list.html',
        {
            'dispatches': dispatches
        }
    )


# @login_required
# def dealer_sale_create(request):

#     profile = DealerProfile.objects.get(
#         admin_user=request.user
#     )

#     dealer = profile.dealer

#     products = Product.objects.filter(
#         is_active=True
#     )

#     customers = DealerCustomer.objects.filter(
#         dealer=dealer
#     )

#     if request.method == "POST":

#         customer_id = request.POST.get(
#             'customer'
#         )

#         invoice_no = request.POST.get(
#             'invoice_no'
#         )

#         sale_date = request.POST.get(
#             'sale_date'
#         )

#         paid_amount = Decimal(
#             request.POST.get(
#                 'paid_amount',
#                 0
#             ) or 0
#         )

#         customer = DealerCustomer.objects.get(
#             id=customer_id
#         )

#         sale = DealerSale.objects.create(
#             dealer=dealer,
#             customer=customer,
#             invoice_no=invoice_no,
#             sale_date=sale_date,
#             paid_amount=paid_amount
#         )

#         total_amount = Decimal('0')

#         product_ids = request.POST.getlist(
#             'product[]'
#         )

#         for product_id in product_ids:

#             qty = Decimal(
#                 request.POST.get(
#                     f'qty_{product_id}',
#                     0
#                 ) or 0
#             )

#             rate = Decimal(
#                 request.POST.get(
#                     f'rate_{product_id}',
#                     0
#                 ) or 0
#             )

#             if qty <= 0:
#                 continue

#             product = Product.objects.get(
#                 id=product_id
#             )

#             stock = DealerStock.objects.get(
#                 dealer=dealer,
#                 product=product
#             )

#             if stock.quantity < qty:

#                 sale.delete()

#                 return render(
#                     request,
#                     'dealer_portal/sale_create.html',
#                     {
#                         'products': products,
#                         'customers': customers,
#                         'error':
#                         f'Insufficient stock for '
#                         f'{product.name}'
#                     }
#                 )

#             amount = qty * rate

#             DealerSaleItem.objects.create(
#                 sale=sale,
#                 product=product,
#                 quantity=qty,
#                 rate=rate,
#                 amount=amount
#             )

#             stock.quantity -= qty
#             stock.save()

#             total_amount += amount

#         sale.total_amount = total_amount
#         sale.due_amount = (
#             total_amount -
#             paid_amount
#         )

#         sale.save()

#         balance = add_customer_ledger(
#             customer=customer,
#             entry_type="SALE",
#             debit=total_amount
#         )

#         if paid_amount > 0:

#             balance = add_customer_ledger(
#                 customer=customer,
#                 entry_type="PAYMENT",
#                 credit=paid_amount
#             )

#         sale.due_amount = balance
#         sale.save()

#         return redirect(
#             'dealer_sale_list'
#         )

#     stocks = DealerStock.objects.filter(
#     dealer=dealer
# )

#     return render(
#         request,
#         'dealer_portal/sale_create.html',
#         {
#             'products': products,
#             'customers': customers,
#             'stocks': stocks
#         }
#     )


from django.db import transaction

@login_required
@transaction.atomic
def dealer_sale_create(request):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    products = Product.objects.filter(
        is_active=True
    ).order_by("name")

    customers = DealerCustomer.objects.filter(
        dealer=dealer
    ).order_by("name")

    stocks = (
        DealerStock.objects
        .filter(
            dealer=dealer
        )
        .select_related("product")
    )

    if request.method == "POST":

        customer_id = request.POST.get(
            "customer"
        )

        invoice_no = request.POST.get(
            "invoice_no"
        )

        sale_date = request.POST.get(
            "sale_date"
        )

        paid_amount = Decimal(
            request.POST.get(
                "paid_amount",
                "0"
            ) or "0"
        )

        # -----------------------------------------
        # CUSTOMER
        # -----------------------------------------

        customer = get_object_or_404(
            DealerCustomer,
            id=customer_id,
            dealer=dealer
        )

        # -----------------------------------------
        # BASIC PAYMENT VALIDATION
        # -----------------------------------------

        if paid_amount < 0:

            return render(
                request,
                "dealer_portal/sale_create.html",
                {
                    "products": products,
                    "customers": customers,
                    "stocks": stocks,
                    "error":
                        "Paid amount cannot be negative."
                }
            )

        # -----------------------------------------
        # CREATE SALE
        # -----------------------------------------

        sale = DealerSale.objects.create(
            dealer=dealer,
            customer=customer,
            invoice_no=invoice_no,
            sale_date=sale_date,
            paid_amount=paid_amount
        )

        total_amount = Decimal("0")

        total_bonus_quantity = Decimal("0")

        product_ids = request.POST.getlist(
            "product[]"
        )

        # -----------------------------------------
        # PRODUCTS
        # -----------------------------------------

        for product_id in product_ids:

            qty = Decimal(
                request.POST.get(
                    f"qty_{product_id}",
                    "0"
                ) or "0"
            )

            bonus_qty = Decimal(
                request.POST.get(
                    f"bonus_{product_id}",
                    "0"
                ) or "0"
            )

            rate = Decimal(
                request.POST.get(
                    f"rate_{product_id}",
                    "0"
                ) or "0"
            )

            # Nothing entered
            if qty <= 0 and bonus_qty <= 0:
                continue

            # -------------------------------------
            # VALIDATION
            # -------------------------------------

            if qty < 0:

                return render(
                    request,
                    "dealer_portal/sale_create.html",
                    {
                        "products": products,
                        "customers": customers,
                        "stocks": stocks,
                        "error":
                            "Sale quantity cannot be negative."
                    }
                )

            if bonus_qty < 0:

                return render(
                    request,
                    "dealer_portal/sale_create.html",
                    {
                        "products": products,
                        "customers": customers,
                        "stocks": stocks,
                        "error":
                            "Bonus quantity cannot be negative."
                    }
                )

            if rate < 0:

                return render(
                    request,
                    "dealer_portal/sale_create.html",
                    {
                        "products": products,
                        "customers": customers,
                        "stocks": stocks,
                        "error":
                            "Rate cannot be negative."
                    }
                )

            # -------------------------------------
            # PRODUCT
            # -------------------------------------

            product = get_object_or_404(
                Product,
                id=product_id,
                is_active=True
            )

            # -------------------------------------
            # DEALER STOCK
            # -------------------------------------

            stock = (
                DealerStock.objects
                .filter(
                    dealer=dealer,
                    product=product
                )
                .first()
            )

            if not stock:

                return render(
                    request,
                    "dealer_portal/sale_create.html",
                    {
                        "products": products,
                        "customers": customers,
                        "stocks": stocks,
                        "error":
                            f"No stock found for "
                            f"{product.name}"
                    }
                )

            # -------------------------------------
            # PHYSICAL STOCK
            # -------------------------------------
            #
            # Sale + Bonus both consume physical stock.
            #

            total_stock_required = (
                qty +
                bonus_qty
            )

            if stock.quantity < total_stock_required:

                return render(
                    request,
                    "dealer_portal/sale_create.html",
                    {
                        "products": products,
                        "customers": customers,
                        "stocks": stocks,
                        "error":
                            f"Insufficient stock for "
                            f"{product.name}. "
                            f"Available: {stock.quantity}, "
                            f"Required: "
                            f"{total_stock_required}"
                    }
                )

            # -------------------------------------
            # AMOUNT
            # -------------------------------------
            #
            # IMPORTANT:
            # Bonus is FREE.
            # Only normal sale quantity is charged.
            #

            amount = qty * rate

            # -------------------------------------
            # CREATE SALE ITEM
            # -------------------------------------

            DealerSaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=qty,
                bonus_quantity=bonus_qty,
                rate=rate,
                amount=amount
            )

            # -------------------------------------
            # DEDUCT PHYSICAL STOCK
            # -------------------------------------

            stock.quantity -= (
                qty +
                bonus_qty
            )

            stock.save()

            # -------------------------------------
            # TOTALS
            # -------------------------------------

            total_amount += amount

            total_bonus_quantity += bonus_qty

        # -----------------------------------------
        # SALE TOTALS
        # -----------------------------------------

        sale.total_amount = total_amount

        sale.due_amount = (
            total_amount -
            paid_amount
        )

        sale.save()

        # -----------------------------------------
        # CUSTOMER LEDGER - DEALER SALE
        # -----------------------------------------
        #
        # IMPORTANT:
        # We now send total_bonus_quantity here.
        #

        balance = add_customer_ledger(
            customer=customer,
            entry_type="DEALER_SALE",
            debit=total_amount,
            bonus_quantity=total_bonus_quantity
        )

        # -----------------------------------------
        # CUSTOMER LEDGER - PAYMENT
        # -----------------------------------------

        if paid_amount > 0:

            balance = add_customer_ledger(
                customer=customer,
                entry_type="PAYMENT",
                credit=paid_amount
            )

        # -----------------------------------------
        # FINAL DUE AMOUNT
        # -----------------------------------------

        sale.due_amount = balance

        sale.save()

        return redirect(
            "dealer_sale_list"
        )

    # ---------------------------------------------
    # GET
    # ---------------------------------------------

    return render(
        request,
        "dealer_portal/sale_create.html",
        {
            "products": products,
            "customers": customers,
            "stocks": stocks
        }
    )


@login_required
def dealer_sale_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    sales = DealerSale.objects.filter(
        dealer=profile.dealer
    ).order_by(
        '-id'
    )

    return render(
        request,
        'dealer_portal/sale_list.html',
        {
            'sales': sales
        }
    )


@login_required
def dealer_sales_return_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    returns = DealerSalesReturn.objects.filter(
        dealer=profile.dealer
    ).order_by('-id')

    return render(
        request,
        'dealer_portal/sales_return_list.html',
        {
            'returns': returns
        }
    )


@login_required
def dealer_sales_return_create(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dealer = profile.dealer

    sales = DealerSale.objects.filter(
        dealer=dealer
    )

    if request.method == "POST":

        sale_id = request.POST.get(
            "sale"
        )

        return_no = request.POST.get(
            "return_no"
        )

        return_date = request.POST.get(
            "return_date"
        )

        sale = DealerSale.objects.get(
            id=sale_id,
            dealer=dealer
        )

        sales_return = DealerSalesReturn.objects.create(
            dealer=dealer,
            sale=sale,
            return_no=return_no,
            return_date=return_date
        )

        total_return = Decimal("0")

        for item in sale.items.all():

            qty = Decimal(
                request.POST.get(
                    f"return_qty_{item.id}",
                    0
                ) or 0
            )

            if qty <= 0:
                continue

            # -----------------------------
            # Prevent over return
            # -----------------------------
            already_returned = (
                DealerSalesReturnItem.objects.filter(
                    sale_item=item
                ).aggregate(
                    total=Sum("return_qty")
                )["total"] or Decimal("0")
            )

            available_qty = (
                item.quantity -
                already_returned
            )

            if qty > available_qty:

                sales_return.delete()

                return render(
                    request,
                    "dealer_portal/sales_return_create.html",
                    {
                        "sales": sales,
                        "error":
                        f"You can return only {available_qty} of {item.product.name}."
                    }
                )

            amount = qty * item.rate

            DealerSalesReturnItem.objects.create(
                sales_return=sales_return,
                sale_item=item,
                product=item.product,
                return_qty=qty,
                rate=item.rate,
                amount=amount
            )

            stock, created = DealerStock.objects.get_or_create(
                dealer=dealer,
                product=item.product,
                defaults={
                    "quantity": Decimal("0")
                }
            )

            stock.quantity += qty
            stock.save()

            total_return += amount

        # -----------------------------
        # Save Return
        # -----------------------------
        sales_return.total_return_amount = total_return
        sales_return.save()

        # -----------------------------
        # Update Sale Due
        # -----------------------------
        if total_return >= sale.due_amount:

            sale.due_amount = Decimal("0")

        else:

            sale.due_amount -= total_return

        sale.save()

        # -----------------------------
        # Update Customer Ledger
        # -----------------------------
        add_customer_ledger(
            customer=sale.customer,
            entry_type="SALES_RETURN",
            credit=total_return
        )

        return redirect(
            "dealer_sales_return_list"
        )

    return render(
        request,
        "dealer_portal/sales_return_create.html",
        {
            "sales": sales
        }
    )


@login_required
def dealer_customer_payment_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    payments = DealerCustomerPayment.objects.filter(
        dealer=profile.dealer
    ).order_by('-id')

    return render(
        request,
        'dealer_portal/customer_payment_list.html',
        {
            'payments': payments
        }
    )

@login_required
def dealer_customer_payment_create(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dealer = profile.dealer

    customers = DealerCustomer.objects.filter(
        dealer=dealer,
        is_active=True
    )

    if request.method == "POST":

        customer = DealerCustomer.objects.get(
            id=request.POST.get("customer")
        )

        amount = Decimal(
            request.POST.get(
                "amount",
                0
            ) or 0
        )

        payment_date = request.POST.get(
            "payment_date"
        )

        DealerCustomerPayment.objects.create(
            dealer=dealer,
            customer=customer,
            amount=amount,
            payment_date=payment_date
        )

        remaining = amount

        sales = DealerSale.objects.filter(
            dealer=dealer,
            customer=customer,
            due_amount__gt=0
        ).order_by(
            "sale_date",
            "id"
        )

        for sale in sales:

            if remaining <= 0:
                break

            if remaining >= sale.due_amount:

                remaining -= sale.due_amount

                sale.due_amount = Decimal("0")

            else:

                sale.due_amount -= remaining

                remaining = Decimal("0")

            sale.save()

        add_customer_ledger(
            customer=customer,
            entry_type="PAYMENT",
            credit=amount
        )

        return redirect(
            "dealer_customer_payment_list"
        )

    return render(
        request,
        "dealer_portal/customer_payment_create.html",
        {
            "customers": customers
        }
    )

@login_required
def dealer_customer_ledger_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    customers = DealerCustomer.objects.filter(
        dealer=profile.dealer,
        is_active=True
    )

    return render(
        request,
        'dealer_portal/customer_ledger_list.html',
        {
            'customers': customers
        }
    )


@login_required
def dealer_customer_ledger_detail(
    request,
    customer_id
):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    customer = get_object_or_404(
        DealerCustomer,
        id=customer_id,
        dealer=profile.dealer
    )

    ledger_entries = (
        DealerCustomerLedger.objects
        .filter(
            customer=customer
        )
        .order_by("id")
    )

    total_debit = sum(
        (
            entry.debit
            for entry in ledger_entries
        ),
        Decimal("0")
    )

    total_credit = sum(
        (
            entry.credit
            for entry in ledger_entries
        ),
        Decimal("0")
    )

    total_bonus = sum(
        (
            entry.bonus_quantity
            for entry in ledger_entries
        ),
        Decimal("0")
    )

    last_entry = ledger_entries.last()

    balance = (
        last_entry.balance
        if last_entry
        else Decimal("0")
    )

    return render(
        request,
        "dealer_portal/customer_ledger_detail.html",
        {
            "customer": customer,
            "ledger_entries": ledger_entries,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "total_bonus": total_bonus,
            "balance": balance
        }
    )


# @login_required
# def dealer_outstanding_report(request):

#     profile = DealerProfile.objects.get(
#         admin_user=request.user
#     )

#     dealer = profile.dealer

#     customers = DealerCustomer.objects.filter(
#         dealer=dealer,
#         is_active=True
#     )

#     report = []

#     for customer in customers:

#         sales_total = (
#             DealerSale.objects.filter(
#                 dealer=dealer,
#                 customer=customer
#             ).aggregate(
#                 total=Sum('total_amount')
#             )['total'] or 0
#         )

#         payments_total = (
#             DealerCustomerPayment.objects.filter(
#                 dealer=dealer,
#                 customer=customer
#             ).aggregate(
#                 total=Sum('amount')
#             )['total'] or 0
#         )

#         returns_total = (
#             DealerSalesReturn.objects.filter(
#                 dealer=dealer,
#                 sale__customer=customer
#             ).aggregate(
#                 total=Sum('total_return_amount')
#             )['total'] or 0
#         )

#         outstanding = (
#             sales_total
#             - payments_total
#             - returns_total
#         )

#         report.append({
#             'customer': customer,
#             'sales': sales_total,
#             'payments': payments_total,
#             'returns': returns_total,
#             'outstanding': outstanding
#         })

#     return render(
#         request,
#         'dealer_portal/outstanding_report.html',
#         {
#             'report': report
#         }
#     )



@login_required
def vehicle_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    vehicles = DealerVehicle.objects.filter(
        dealer=profile.dealer
    ).order_by(
        'vehicle_no'
    )

    return render(
        request,
        'dealer_portal/vehicle_list.html',
        {
            'vehicles': vehicles
        }
    )



@login_required
def vehicle_create(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    if request.method == 'POST':

        form = DealerVehicleForm(
            request.POST
        )

        if form.is_valid():

            vehicle = form.save(
                commit=False
            )

            vehicle.dealer = (
                profile.dealer
            )

            vehicle.save()

            return redirect(
                'vehicle_list'
            )

    else:

        form = DealerVehicleForm()

    return render(
        request,
        'dealer_portal/vehicle_create.html',
        {
            'form': form
        }
    )


@login_required
def vehicle_dispatch_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dispatches = VehicleDispatch.objects.filter(
        dealer=profile.dealer
    ).select_related(
        'vehicle'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'dealer_portal/vehicle_dispatch_list.html',
        {
            'dispatches': dispatches
        }
    )


@login_required
def vehicle_dispatch_create(request):

    # -----------------------------------
    # Dealer Profile
    # -----------------------------------

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    # -----------------------------------
    # Active Vehicles
    # -----------------------------------

    vehicles = DealerVehicle.objects.filter(
        dealer=dealer,
        is_active=True
    ).order_by("vehicle_no")

    # -----------------------------------
    # POST
    # -----------------------------------

    if request.method == "POST":

        vehicle_id = request.POST.get("vehicle")
        driver_name = request.POST.get("driver_name", "").strip()

        # -------------------------------
        # Validate Vehicle
        # -------------------------------

        if not vehicle_id:
            return render(
                request,
                "dealer_portal/vehicle_dispatch_create.html",
                {
                    "vehicles": vehicles,
                    "error": "Please select a vehicle."
                }
            )

        vehicle = get_object_or_404(
            DealerVehicle,
            id=vehicle_id,
            dealer=dealer,
            is_active=True
        )

        # -------------------------------
        # Driver Name
        # -------------------------------

        if not driver_name:

            # If no driver was manually entered,
            # use the driver's name stored against vehicle.

            driver_name = (
                getattr(vehicle, "driver_name", "")
                or ""
            ).strip()

        # -------------------------------
        # Current Date & Time
        # -------------------------------

        now = timezone.localtime()

        dispatch_date = now.date()
        dispatch_time = now.time()

        # -------------------------------
        # Check Existing Open Dispatch
        # -------------------------------

        dispatch = VehicleDispatch.objects.filter(
            dealer=dealer,
            vehicle=vehicle,
            dispatch_date=dispatch_date,
            status="OPEN"
        ).first()

        if dispatch:

            return redirect(
                "vehicle_dispatch_detail",
                dispatch.id
            )

        # -------------------------------
        # Generate Dispatch Number
        # -------------------------------

        last_dispatch = (
            VehicleDispatch.objects
            .order_by("-id")
            .first()
        )

        if last_dispatch:
            dispatch_number = last_dispatch.id + 1
        else:
            dispatch_number = 1

        dispatch_no = f"VD-{dispatch_number}"

        # -------------------------------
        # Create Dispatch
        # -------------------------------

        dispatch = VehicleDispatch.objects.create(

            dealer=dealer,

            vehicle=vehicle,

            dispatch_no=dispatch_no,

            dispatch_date=dispatch_date,

            dispatch_time=dispatch_time,

            driver_name=driver_name,

            status="OPEN"
        )

        return redirect(
            "vehicle_dispatch_detail",
            dispatch.id
        )

    # -----------------------------------
    # GET
    # -----------------------------------

    return render(
        request,
        "dealer_portal/vehicle_dispatch_create.html",
        {
            "vehicles": vehicles
        }
    )

# @login_required
# def vehicle_dispatch_close(request, pk):

#     profile = DealerProfile.objects.get(
#         admin_user=request.user
#     )

#     dispatch = get_object_or_404(
#         VehicleDispatch,
#         pk=pk,
#         dealer=profile.dealer
#     )

#     if request.method == 'POST':

#         for item in dispatch.items.all():

#             sold_qty = Decimal(
#                 request.POST.get(
#                     f'sold_{item.id}',
#                     0
#                 ) or 0
#             )

#             return_qty = Decimal(
#                 request.POST.get(
#                     f'return_{item.id}',
#                     0
#                 ) or 0
#             )

#             breakage_qty = Decimal(
#                 request.POST.get(
#                     f'breakage_{item.id}',
#                     0
#                 ) or 0
#             )

#             leakage_qty = Decimal(
#                 request.POST.get(
#                     f'leakage_{item.id}',
#                     0
#                 ) or 0
#             )

#             sponsor_qty = Decimal(
#                 request.POST.get(
#                     f'sponsor_{item.id}',
#                     0
#                 ) or 0
#             )

#             total = (
#                 sold_qty +
#                 return_qty +
#                 breakage_qty +
#                 leakage_qty +
#                 sponsor_qty
#             )

#             if total > item.dispatch_qty:

#                 return render(
#                     request,
#                     'dealer_portal/vehicle_dispatch_close.html',
#                     {
#                         'dispatch': dispatch,
#                         'error': f'Total exceeds dispatched quantity for {item.product.name}'
#                     }
#                 )

#             # Save dispatch result
#             item.sold_qty = sold_qty
#             item.return_qty = return_qty
#             item.breakage_qty = breakage_qty
#             item.leakage_qty = leakage_qty
#             item.sponsor_qty = sponsor_qty

#             item.save()

#             # Returned stock goes back to dealer stock
#             if return_qty > 0:

#                 stock, created = DealerStock.objects.get_or_create(
#                     dealer=profile.dealer,
#                     product=item.product,
#                     defaults={
#                         'quantity': Decimal('0')
#                     }
#                 )

#                 stock.quantity += return_qty
#                 stock.save()

#             # Save sponsor history
#             if sponsor_qty > 0:

#                 DealerSponsor.objects.create(

#                     dealer=profile.dealer,

#                     vehicle=dispatch.vehicle,

#                     vehicle_dispatch=dispatch,

#                     product=item.product,

#                     quantity=sponsor_qty,

#                     sponsor_date=date.today(),

#                     source='VEHICLE',

#                     remarks=f"Vehicle Dispatch {dispatch.dispatch_no}"

#                 )

#         dispatch.status = 'CLOSED'
#         dispatch.save()

#         return redirect(
#             'vehicle_dispatch_list'
#         )

#     return render(
#         request,
#         'dealer_portal/vehicle_dispatch_close.html',
#         {
#             'dispatch': dispatch
#         }
#     )

@login_required
def vehicle_dispatch_close(request, pk):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    dispatch = get_object_or_404(
        VehicleDispatch,
        pk=pk,
        dealer=dealer
    )

    # ==========================================
    # GET ALL TRIPS
    # ==========================================

    trips = dispatch.trips.prefetch_related(
        "items__product"
    ).order_by(
        "trip_no"
    )

    # ==========================================
    # IMPORTANT:
    # ALL TRIPS MUST BE CLOSED FIRST
    # ==========================================

    open_trips = trips.filter(
        is_closed=False
    )

    if open_trips.exists():

        return render(
            request,
            "dealer_portal/vehicle_dispatch_close.html",
            {
                "dispatch": dispatch,
                "trips": trips,
                "open_trips": open_trips,
                "error":
                    "All vehicle trips must be closed "
                    "before closing this dispatch."
            }
        )

    # ==========================================
    # BUILD DISPATCH SUMMARY
    # ==========================================

    summary = {}

    for trip in trips:

        for item in trip.items.all():

            pid = item.product.id

            if pid not in summary:

                summary[pid] = {

                    "product": item.product,

                    "loaded": Decimal("0"),

                    "sold": Decimal("0"),

                    "bonus": Decimal("0"),

                    "returned": Decimal("0"),

                    "breakage": Decimal("0"),

                    "leakage": Decimal("0"),

                    "sponsor": Decimal("0"),

                    "sales_amount": Decimal("0"),

                    "trip_items": []

                }

            row = summary[pid]

            row["loaded"] += item.dispatch_qty

            row["sold"] += item.sold_qty

            row["bonus"] += item.bonus_qty

            row["returned"] += item.return_qty

            row["breakage"] += item.breakage_qty

            row["leakage"] += item.leakage_qty

            row["sponsor"] += item.sponsor_qty

            row["sales_amount"] += item.sales_amount

            row["trip_items"].append(item)

    # ==========================================
    # FINAL RECONCILIATION
    # ==========================================

    for pid, row in summary.items():

        accounted = (

            row["sold"]
            + row["bonus"]
            + row["returned"]
            + row["breakage"]
            + row["leakage"]
            + row["sponsor"]
        )

        row["accounted"] = accounted

        row["matched"] = (
            accounted == row["loaded"]
        )

    # ==========================================
    # CLOSE DISPATCH
    # ==========================================

    if request.method == "POST":

        # --------------------------------------
        # Make sure everything matches
        # --------------------------------------

        for pid, row in summary.items():

            if row["accounted"] != row["loaded"]:

                return render(
                    request,
                    "dealer_portal/vehicle_dispatch_close.html",
                    {
                        "dispatch": dispatch,
                        "trips": trips,
                        "summary": summary.values(),
                        "error":
                            f"{row['product'].name}: "
                            f"Loaded {row['loaded']} but "
                            f"accounted {row['accounted']}. "
                            f"All quantities must match."
                    }
                )

        # --------------------------------------
        # Close dispatch
        # --------------------------------------

        dispatch.status = "CLOSED"

        dispatch.return_date = date.today()

        dispatch.save()

        return redirect(
            "vehicle_dispatch_list"
        )

    # ==========================================
    # GET
    # ==========================================

    return render(
        request,
        "dealer_portal/vehicle_dispatch_close.html",
        {
            "dispatch": dispatch,
            "trips": trips,
            "summary": summary.values()
        }
    )



@login_required
def vehicle_dispatch_report(request, pk):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dispatch = get_object_or_404(
        VehicleDispatch,
        pk=pk,
        dealer=profile.dealer
    )

    trips = dispatch.trips.prefetch_related(
        "items__product"
    )

    sales = dispatch.sales.select_related(
        "product"
    )

    summary = {}

    grand_total = Decimal("0")

    grand_qty = Decimal("0")

    # -----------------------
    # Trip Summary
    # -----------------------

    for trip in trips:

        for item in trip.items.all():

            pid = item.product.id

            if pid not in summary:

                summary[pid] = {

                    "product": item.product,

                    "loaded": Decimal("0"),

                    "sold": Decimal("0"),

                    "returned": Decimal("0"),

                    "breakage": Decimal("0"),

                    "leakage": Decimal("0"),

                    "sponsor": Decimal("0"),

                    "sales_amount": Decimal("0"),

                    "sales_qty": Decimal("0"),

                    "sales": []

                }

            row = summary[pid]

            row["loaded"] += item.dispatch_qty
            row["sold"] += item.sold_qty
            row["returned"] += item.return_qty
            row["breakage"] += item.breakage_qty
            row["leakage"] += item.leakage_qty
            row["sponsor"] += item.sponsor_qty

    # -----------------------
    # Sales
    # -----------------------

    for sale in sales:

        pid = sale.product.id

        if pid not in summary:

            summary[pid] = {

                "product": sale.product,

                "loaded": Decimal("0"),

                "sold": Decimal("0"),

                "returned": Decimal("0"),

                "breakage": Decimal("0"),

                "leakage": Decimal("0"),

                "sponsor": Decimal("0"),

                "sales_amount": Decimal("0"),

                "sales_qty": Decimal("0"),

                "sales": []

            }

        summary[pid]["sales"].append(sale)

        summary[pid]["sales_qty"] += sale.quantity

        summary[pid]["sales_amount"] += sale.amount

        grand_total += sale.amount

        grand_qty += sale.quantity

    return render(

        request,

        "dealer_portal/vehicle_dispatch_report.html",

        {

            "dispatch": dispatch,

            "trips": trips,

            "summary": summary.values(),

            "grand_total": grand_total,

            "grand_qty": grand_qty,

        }

    )
@login_required
def vehicle_trip_detail(request, trip_id):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    trip = get_object_or_404(
        VehicleTrip.objects.prefetch_related(
            "items__product"
        ),
        id=trip_id,
        dispatch__dealer=profile.dealer
    )

    return render(
        request,
        "dealer_portal/vehicle_trip_detail.html",
        {
            "trip": trip
        }
    )





#now its working for vehicle dispatch for dealer for latesst update
@login_required
def vehicle_dispatch_detail(request, pk):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dispatch = get_object_or_404(
        VehicleDispatch,
        id=pk,
        dealer=profile.dealer
    )

    trips = VehicleTrip.objects.filter(
        dispatch=dispatch
    ).order_by("trip_no")

    context = {

        "dispatch": dispatch,

        "trips": trips,

    }

    return render(
        request,
        "dealer_portal/vehicle_dispatch_detail.html",
        context
    )


@login_required
def vehicle_trip_create(request, dispatch_id):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dispatch = get_object_or_404(
        VehicleDispatch,
        id=dispatch_id,
        dealer=profile.dealer,
        status="OPEN"
    )

    stocks = DealerStock.objects.filter(
        dealer=profile.dealer
    ).select_related("product")

    if request.method == "POST":

        trip = VehicleTrip.objects.create(
            dispatch=dispatch,
            trip_no=dispatch.trips.count() + 1
        )

        for stock in stocks:

            qty = Decimal(
                request.POST.get(
                    f"qty_{stock.product.id}",
                    0
                ) or 0
            )

            if qty <= 0:
                continue

            if qty > stock.quantity:

                trip.delete()

                return render(
                    request,
                    "dealer_portal/vehicle_trip_create.html",
                    {
                        "dispatch": dispatch,
                        "stocks": stocks,
                        "error": f"Not enough stock for {stock.product.name}"
                    }
                )

            VehicleTripItem.objects.create(
                trip=trip,
                product=stock.product,
                dispatch_qty=qty
            )

            stock.quantity -= qty
            stock.save()

        return redirect(
            "vehicle_dispatch_detail",
            dispatch.id
        )

    return render(
        request,
        "dealer_portal/vehicle_trip_create.html",
        {
            "dispatch": dispatch,
            "stocks": stocks
        }
    )


@login_required
@transaction.atomic
def vehicle_trip_close(request, trip_id):

    # =====================================================
    # DEALER PROFILE
    # =====================================================

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    # =====================================================
    # GET TRIP
    # =====================================================

    trip = get_object_or_404(
        VehicleTrip.objects
        .select_related(
            "dispatch",
            "dispatch__vehicle"
        )
        .prefetch_related(
            "items__product"
        ),
        id=trip_id,
        dispatch__dealer=dealer
    )

    # =====================================================
    # CUSTOMERS
    # =====================================================

    customers = (
        DealerCustomer.objects
        .filter(
            dealer=dealer
        )
        .order_by("name")
    )

    # =====================================================
    # ALREADY CLOSED
    # =====================================================

    if trip.is_closed:

        return redirect(
            "vehicle_trip_detail",
            trip.id
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # =================================================
        # IMPORTANT
        #
        # We DO NOT create:
        #
        # VehicleDispatchSale
        # DealerCustomerLedger
        #
        # yet.
        #
        # First validate the COMPLETE trip.
        # =================================================

        validated_sales = []

        # =================================================
        # PROCESS EVERY PRODUCT
        # =================================================

        for item in trip.items.all():

            # ---------------------------------------------
            # SALES INPUT
            # ---------------------------------------------

            sale_customers = request.POST.getlist(
                f"sale_customer_{item.id}[]"
            )

            sale_quantities = request.POST.getlist(
                f"sale_qty_{item.id}[]"
            )

            sale_bonuses = request.POST.getlist(
                f"sale_bonus_{item.id}[]"
            )

            sale_rates = request.POST.getlist(
                f"sale_rate_{item.id}[]"
            )

            # ---------------------------------------------
            # PRODUCT TOTALS
            # ---------------------------------------------

            product_sold = Decimal("0")

            product_bonus = Decimal("0")

            product_sales_amount = Decimal("0")

            # ---------------------------------------------
            # VALIDATE SALES
            # ---------------------------------------------

            for i in range(
                len(sale_quantities)
            ):

                # =========================================
                # QUANTITY
                # =========================================

                try:

                    qty = Decimal(
                        sale_quantities[i]
                        or "0"
                    )

                except Exception:

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Invalid sale quantity "
                                f"for {item.product.name}."
                        }
                    )

                # =========================================
                # BONUS
                # =========================================

                try:

                    bonus = Decimal(
                        sale_bonuses[i]
                        if (
                            i < len(sale_bonuses)
                            and sale_bonuses[i]
                        )
                        else "0"
                    )

                except Exception:

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Invalid bonus quantity "
                                f"for {item.product.name}."
                        }
                    )

                # =========================================
                # RATE
                # =========================================

                try:

                    rate = Decimal(
                        sale_rates[i]
                        if (
                            i < len(sale_rates)
                            and sale_rates[i]
                        )
                        else "0"
                    )

                except Exception:

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Invalid rate "
                                f"for {item.product.name}."
                        }
                    )

                # =========================================
                # NEGATIVE CHECK
                # =========================================

                if qty < 0:

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Sale quantity cannot be "
                                f"negative for "
                                f"{item.product.name}."
                        }
                    )

                if bonus < 0:

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Bonus quantity cannot be "
                                f"negative for "
                                f"{item.product.name}."
                        }
                    )

                if rate < 0:

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Rate cannot be negative "
                                f"for {item.product.name}."
                        }
                    )

                # =========================================
                # NOTHING ENTERED
                # =========================================

                if qty <= 0 and bonus <= 0:

                    continue

                # =========================================
                # CUSTOMER REQUIRED
                # =========================================

                if (
                    i >= len(sale_customers)
                    or not sale_customers[i]
                ):

                    return render(
                        request,
                        "dealer_portal/vehicle_trip_close.html",
                        {
                            "trip": trip,
                            "customers": customers,
                            "error":
                                f"Please select a customer "
                                f"for {item.product.name}."
                        }
                    )

                # =========================================
                # CUSTOMER
                # =========================================

                customer = get_object_or_404(
                    DealerCustomer,
                    id=sale_customers[i],
                    dealer=dealer
                )

                # =========================================
                # BONUS-ONLY SALE
                #
                # If bonus exists but sale qty is zero,
                # rate is not required.
                # =========================================

                if qty <= 0:

                    rate = Decimal("0")

                # =========================================
                # AMOUNT
                #
                # BONUS IS FREE.
                # =========================================

                amount = (
                    qty * rate
                )

                # =========================================
                # SAVE ONLY IN MEMORY FOR NOW
                #
                # DO NOT CREATE DATABASE RECORD YET.
                # =========================================

                validated_sales.append(
                    {
                        "item": item,
                        "customer": customer,
                        "quantity": qty,
                        "bonus_quantity": bonus,
                        "rate": rate,
                        "amount": amount,
                    }
                )

                product_sold += qty

                product_bonus += bonus

                product_sales_amount += amount

            # =================================================
            # OTHER QUANTITIES
            # =================================================

            try:

                returned = Decimal(
                    request.POST.get(
                        f"return_{item.id}",
                        "0"
                    ) or "0"
                )

                breakage = Decimal(
                    request.POST.get(
                        f"breakage_{item.id}",
                        "0"
                    ) or "0"
                )

                leakage = Decimal(
                    request.POST.get(
                        f"leakage_{item.id}",
                        "0"
                    ) or "0"
                )

                sponsor = Decimal(
                    request.POST.get(
                        f"sponsor_{item.id}",
                        "0"
                    ) or "0"
                )

            except Exception:

                return render(
                    request,
                    "dealer_portal/vehicle_trip_close.html",
                    {
                        "trip": trip,
                        "customers": customers,
                        "error":
                            f"Invalid quantity entered "
                            f"for {item.product.name}."
                    }
                )

            # =================================================
            # NEGATIVE CHECK
            # =================================================

            if (
                returned < 0
                or breakage < 0
                or leakage < 0
                or sponsor < 0
            ):

                return render(
                    request,
                    "dealer_portal/vehicle_trip_close.html",
                    {
                        "trip": trip,
                        "customers": customers,
                        "error":
                            f"Quantities cannot be negative "
                            f"for {item.product.name}."
                    }
                )

            # =================================================
            # EXACT RECONCILIATION
            # =================================================

            total_accounted = (
                product_sold
                + product_bonus
                + returned
                + breakage
                + leakage
                + sponsor
            )

            # =================================================
            # MUST EXACTLY MATCH DISPATCH QTY
            # =================================================

            if total_accounted != item.dispatch_qty:

                return render(
                    request,
                    "dealer_portal/vehicle_trip_close.html",
                    {
                        "trip": trip,
                        "customers": customers,
                        "error":
                            f"{item.product.name}: "
                            f"Loaded = {item.dispatch_qty}, "
                            f"but Sold ({product_sold}) + "
                            f"Bonus ({product_bonus}) + "
                            f"Returned ({returned}) + "
                            f"Breakage ({breakage}) + "
                            f"Leakage ({leakage}) + "
                            f"Sponsor ({sponsor}) = "
                            f"{total_accounted}. "
                            f"These quantities must exactly match."
                    }
                )

            # =================================================
            # SAVE RECONCILIATION DATA IN MEMORY
            # =================================================

            item._close_data = {
                "sold_qty": product_sold,
                "bonus_qty": product_bonus,
                "return_qty": returned,
                "breakage_qty": breakage,
                "leakage_qty": leakage,
                "sponsor_qty": sponsor,
                "sales_amount": product_sales_amount,
            }

        # =====================================================
        # EVERYTHING PASSED VALIDATION
        #
        # ONLY NOW DO WE WRITE TO DATABASE.
        # =====================================================

        # =====================================================
        # CREATE VEHICLE SALES + LEDGER
        # =====================================================

        for sale_data in validated_sales:

            item = sale_data["item"]

            customer = sale_data["customer"]

            qty = sale_data["quantity"]

            bonus = sale_data["bonus_quantity"]

            rate = sale_data["rate"]

            amount = sale_data["amount"]

            # =============================================
            # VEHICLE SALE
            # =============================================

            VehicleDispatchSale.objects.create(

                dispatch=trip.dispatch,

                customer=customer,

                product=item.product,

                quantity=qty,

                bonus_quantity=bonus,

                rate=rate,

                amount=amount

            )

            # =============================================
            # CUSTOMER LEDGER
            #
            # IMPORTANT:
            # This happens ONLY after the ENTIRE trip
            # has passed validation.
            # =============================================

            if amount > 0 or bonus > 0:

                add_customer_ledger(

                    customer=customer,

                    entry_type="VEHICLE_SALE",

                    debit=amount,

                    bonus_quantity=bonus

                )

        # =====================================================
        # UPDATE TRIP ITEMS
        # =====================================================

        for item in trip.items.all():

            data = item._close_data

            item.sold_qty = (
                data["sold_qty"]
            )

            item.bonus_qty = (
                data["bonus_qty"]
            )

            item.return_qty = (
                data["return_qty"]
            )

            item.breakage_qty = (
                data["breakage_qty"]
            )

            item.leakage_qty = (
                data["leakage_qty"]
            )

            item.sponsor_qty = (
                data["sponsor_qty"]
            )

            item.sales_amount = (
                data["sales_amount"]
            )

            item.save()

            # =============================================
            # RETURN STOCK
            # =============================================

            if data["return_qty"] > 0:

                stock, created = (
                    DealerStock.objects
                    .get_or_create(
                        dealer=dealer,
                        product=item.product,
                        defaults={
                            "quantity": Decimal("0")
                        }
                    )
                )

                stock.quantity = (
                    stock.quantity
                    + data["return_qty"]
                )

                stock.save()

            # =============================================
            # SPONSOR HISTORY
            # =============================================

            if data["sponsor_qty"] > 0:

                DealerSponsor.objects.create(

                    dealer=dealer,

                    vehicle=trip.dispatch.vehicle,

                    vehicle_dispatch=trip.dispatch,

                    product=item.product,

                    quantity=data["sponsor_qty"],

                    sponsor_date=date.today(),

                    source="VEHICLE",

                    remarks=(
                        f"Trip {trip.trip_no}"
                    )

                )

        # =====================================================
        # CLOSE TRIP
        # =====================================================

        trip.is_closed = True

        trip.save()

        # =====================================================
        # SUCCESS
        # =====================================================

        return redirect(
            "vehicle_trip_detail",
            trip.id
        )

    # =========================================================
    # GET
    # =========================================================

    return render(
        request,
        "dealer_portal/vehicle_trip_close.html",
        {
            "trip": trip,
            "customers": customers
        }
    )

@login_required
def sponsor_list(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    sponsors = DealerSponsor.objects.filter(
        dealer=profile.dealer
    ).order_by('-id')

    return render(
        request,
        'dealer_portal/sponsor_list.html',
        {
            'sponsors': sponsors
        }
    )


@login_required
def sponsor_create(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    dealer = profile.dealer

    if request.method == "POST":

        form = DealerSponsorForm(request.POST)

        if form.is_valid():

            sponsor = form.save(commit=False)

            sponsor.dealer = dealer

            sponsor.source = "DEALER"

            stock = DealerStock.objects.get(
                dealer=dealer,
                product=sponsor.product
            )

            if stock.quantity < sponsor.quantity:

                return render(
                    request,
                    "dealer_portal/sponsor_create.html",
                    {
                        "form": form,
                        "error": "Insufficient Stock"
                    }
                )

            stock.quantity -= sponsor.quantity

            stock.save()

            sponsor.save()

            return redirect(
                "sponsor_list"
            )

    else:

        form = DealerSponsorForm()

    return render(
        request,
        "dealer_portal/sponsor_create.html",
        {
            "form": form
        }
    )


@login_required
def dealer_sales_report(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    sales = DealerSale.objects.filter(
        dealer=profile.dealer
    ).order_by('-sale_date')

    total_sales = sales.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_paid = sales.aggregate(
        total=Sum('paid_amount')
    )['total'] or 0

    total_due = sales.aggregate(
        total=Sum('due_amount')
    )['total'] or 0

    return render(
        request,
        'dealer_portal/sales_report.html',
        {
            'sales': sales,
            'total_sales': total_sales,
            'total_paid': total_paid,
            'total_due': total_due
        }
    )


@login_required
def dealer_stock_report(request):

    profile = DealerProfile.objects.get(
        admin_user=request.user
    )

    stocks = DealerStock.objects.filter(
        dealer=profile.dealer
    ).select_related(
        'product'
    )

    return render(
        request,
        'dealer_portal/stock_report.html',
        {
            'stocks': stocks
        }
    )