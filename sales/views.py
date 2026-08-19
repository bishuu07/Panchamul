from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import Customer,Sale,CustomerPayment
from .forms import CustomerForm
from decimal import Decimal
from .forms import SaleForm,CustomerPaymentForm,SalesReturnForm
import json
from django.db.models import Sum
from django.http import JsonResponse

from inventory.models import Product
from sales.utils import add_customer_ledger

from django.contrib.auth.decorators import login_required
from .models import (
    Sale,
    SaleItem,
    CustomerLedger,
    Customer,
    SalesReturn,
    SalesReturnItem
)


@login_required
def customer_list(request):

    customers = Customer.objects.all().order_by(
        '-id'
    )

    return render(
        request,
        'sales/customer_list.html',
        {
            'customers': customers
        }
    )


@login_required
def customer_create(request):

    form = CustomerForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect(
            'customer_list'
        )

    return render(
        request,
        'sales/customer_create.html',
        {
            'form': form
        }
    )

@login_required
def customer_edit(request, pk):

    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    form = CustomerForm(
        request.POST or None,
        instance=customer
    )

    if form.is_valid():

        form.save()

        return redirect(
            'customer_list'
        )

    return render(
        request,
        'sales/customer_create.html',
        {
            'form': form
        }
    )


@login_required
def sale_list(request):

    sales = Sale.objects.select_related(
        'customer'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'sales/sale_list.html',
        {
            'sales': sales
        }
    )
from django.db import transaction
@login_required
@transaction.atomic







@login_required
@transaction.atomic
@login_required
@transaction.atomic
def sale_create(request):

    form = SaleForm(
        request.POST or None
    )

    products = (
        Product.objects
        .filter(is_active=True)
        .order_by("name")
    )

    if request.method == "POST":

        if form.is_valid():

            items_json = request.POST.get(
                "items_json",
                ""
            )

            if not items_json:

                return render(
                    request,
                    "sales/sale_create.html",
                    {
                        "form": form,
                        "products": products,
                        "error":
                            "Add at least one product."
                    }
                )

            try:

                items = json.loads(
                    items_json
                )

            except json.JSONDecodeError:

                return render(
                    request,
                    "sales/sale_create.html",
                    {
                        "form": form,
                        "products": products,
                        "error":
                            "Invalid product data."
                    }
                )

            if not items:

                return render(
                    request,
                    "sales/sale_create.html",
                    {
                        "form": form,
                        "products": products,
                        "error":
                            "Add at least one product."
                    }
                )


            # ==========================================
            # SALE / INVOICE DATA
            # ==========================================

            sale = form.save(
                commit=False
            )

            sale.created_by = request.user


            # Make sure invoice/reference exists

            invoice_no = (
                sale.invoice_no
                or ""
            ).strip()


            if not invoice_no:

                return render(
                    request,
                    "sales/sale_create.html",
                    {
                        "form": form,
                        "products": products,
                        "error":
                            "Invoice number is required."
                    }
                )


            # ==========================================
            # VALIDATE PRODUCTS + STOCK FIRST
            # ==========================================

            total_amount = Decimal("0")

            total_bonus = Decimal("0")


            validated_items = []


            for item in items:

                product_id = item.get(
                    "product"
                )

                qty = Decimal(
                    str(
                        item.get(
                            "quantity",
                            0
                        )
                    )
                )

                bonus_qty = Decimal(
                    str(
                        item.get(
                            "bonus_quantity",
                            0
                        )
                    )
                )

                rate = Decimal(
                    str(
                        item.get(
                            "rate",
                            0
                        )
                    )
                )


                # --------------------------------------
                # Validate quantities
                # --------------------------------------

                if qty < 0:

                    return render(
                        request,
                        "sales/sale_create.html",
                        {
                            "form": form,
                            "products": products,
                            "error":
                                "Sale quantity cannot be negative."
                        }
                    )


                if bonus_qty < 0:

                    return render(
                        request,
                        "sales/sale_create.html",
                        {
                            "form": form,
                            "products": products,
                            "error":
                                "Bonus quantity cannot be negative."
                        }
                    )


                if rate < 0:

                    return render(
                        request,
                        "sales/sale_create.html",
                        {
                            "form": form,
                            "products": products,
                            "error":
                                "Rate cannot be negative."
                        }
                    )


                if qty <= 0 and bonus_qty <= 0:

                    continue


                product = get_object_or_404(
                    Product,
                    id=product_id,
                    is_active=True
                )


                # ======================================
                # IMPORTANT:
                # SALE + BONUS BOTH CONSUME STOCK
                # ======================================

                total_required = (
                    qty +
                    bonus_qty
                )


                if product.current_stock < total_required:

                    return render(
                        request,
                        "sales/sale_create.html",
                        {
                            "form": form,
                            "products": products,
                            "error": (
                                f"Insufficient stock "
                                f"for {product.name}. "
                                f"Available: "
                                f"{product.current_stock}, "
                                f"Required: "
                                f"{total_required}"
                            )
                        }
                    )


                # ======================================
                # MONEY:
                # BONUS IS FREE
                # ======================================

                amount = (
                    qty *
                    rate
                )


                total_amount += amount

                total_bonus += bonus_qty


                validated_items.append(
                    {
                        "product": product,
                        "quantity": qty,
                        "bonus_quantity": bonus_qty,
                        "rate": rate,
                        "amount": amount,
                        "total_required": total_required
                    }
                )


            if not validated_items:

                return render(
                    request,
                    "sales/sale_create.html",
                    {
                        "form": form,
                        "products": products,
                        "error":
                            "Add at least one valid product."
                    }
                )


            # ==========================================
            # SAVE SALE
            # ==========================================

            sale.save()


            # ==========================================
            # CREATE SALE ITEMS
            # ==========================================

            for item in validated_items:

                product = item["product"]

                qty = item["quantity"]

                bonus_qty = item["bonus_quantity"]

                rate = item["rate"]

                amount = item["amount"]

                total_required = item["total_required"]


                SaleItem.objects.create(

                    sale=sale,

                    product=product,

                    quantity=qty,

                    bonus_quantity=bonus_qty,

                    rate=rate,

                    amount=amount

                )


                # ======================================
                # DEDUCT SALE + BONUS
                # ======================================

                product.current_stock -= (
                    total_required
                )

                product.save(
                    update_fields=[
                        "current_stock"
                    ]
                )


            # ==========================================
            # SALE TOTALS
            # ==========================================

            sale.total_amount = (
                total_amount
            )

            sale.due_amount = (
                total_amount -
                sale.paid_amount
            )


            if sale.due_amount <= 0:

                sale.status = "PAID"

            elif sale.paid_amount > 0:

                sale.status = "PARTIAL"

            else:

                sale.status = "UNPAID"


            sale.save()


            # ==========================================
            # CUSTOMER LEDGER - SALE
            # ==========================================

            last_entry = (
                CustomerLedger.objects
                .filter(
                    customer=sale.customer
                )
                .order_by("-id")
                .first()
            )


            previous_balance = (

                last_entry.balance

                if last_entry

                else Decimal("0")

            )


            sale_balance = (
                previous_balance +
                total_amount
            )


            CustomerLedger.objects.create(

                customer=sale.customer,

                entry_type="SALE",

                debit=total_amount,

                credit=Decimal("0"),

                bonus_quantity=total_bonus,

                balance=sale_balance,

                # IMPORTANT
                reference=invoice_no,

                remarks="Company Sale"

            )


            # ==========================================
            # CUSTOMER LEDGER - PAYMENT
            # ==========================================

            if sale.paid_amount > 0:

                payment_balance = (
                    sale_balance -
                    sale.paid_amount
                )


                CustomerLedger.objects.create(

                    customer=sale.customer,

                    entry_type="PAYMENT",

                    debit=Decimal("0"),

                    credit=sale.paid_amount,

                    bonus_quantity=Decimal("0"),

                    balance=payment_balance,

                    # IMPORTANT
                    reference=invoice_no,

                    remarks="Company Sale Payment"

                )


                sale.due_amount = (
                    payment_balance
                )

                sale.save(
                    update_fields=[
                        "due_amount"
                    ]
                )


            else:

                sale.due_amount = (
                    sale_balance
                )

                sale.save(
                    update_fields=[
                        "due_amount"
                    ]
                )


            return redirect(
                "sale_list"
            )


    return render(
        request,
        "sales/sale_create.html",
        {
            "form": form,
            "products": products
        }
    )



@login_required
def customer_payment_create(request):

    form = CustomerPaymentForm(
        request.POST or None
    )

    if form.is_valid():

        payment = form.save(
            commit=False
        )

        payment.created_by = request.user

        payment.save()

        last_ledger = CustomerLedger.objects.filter(
            customer=payment.customer
        ).order_by(
            '-id'
        ).first()

        balance = (
            last_ledger.balance
            if last_ledger
            else Decimal('0')
        )

        balance -= payment.amount

        CustomerLedger.objects.create(
            customer=payment.customer,
            entry_type='PAYMENT',
            debit=Decimal('0'),
            credit=payment.amount,
            balance=balance,
            reference=f'PAY-{payment.id}'
        )

        return redirect(
            'customer_payment_list'
        )

    return render(
        request,
        'sales/customer_payment_create.html',
        {
            'form': form
        }
    )


@login_required
def customer_payment_list(request):

    payments = CustomerPayment.objects.select_related(
        'customer'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'sales/customer_payment_list.html',
        {
            'payments': payments
        }
    )


@login_required
def customer_ledger_list(request):

    customers = Customer.objects.all()

    data = []

    for customer in customers:

        debit = CustomerLedger.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('debit')
        )['total'] or 0

        credit = CustomerLedger.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('credit')
        )['total'] or 0

        balance = debit - credit

        data.append({

            'customer': customer,
            'debit': debit,
            'credit': credit,
            'balance': balance

        })

    return render(
        request,
        'sales/customer_ledger_list.html',
        {
            'data': data
        }
    )

@login_required
def customer_ledger_detail(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    ledgers = (
        CustomerLedger.objects
        .filter(customer=customer)
        .order_by("id")
    )

    total_debit = sum(
        (
            row.debit
            for row in ledgers
        ),
        Decimal("0")
    )

    total_credit = sum(
        (
            row.credit
            for row in ledgers
        ),
        Decimal("0")
    )

    total_bonus = sum(
        (
            row.bonus_quantity
            for row in ledgers
        ),
        Decimal("0")
    )

    last_entry = ledgers.last()

    balance = (
        last_entry.balance
        if last_entry
        else Decimal("0")
    )

    return render(
        request,
        "sales/customer_ledger_detail.html",
        {
            "customer": customer,
            "ledgers": ledgers,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "total_bonus": total_bonus,
            "balance": balance,
        }
    )


@login_required
def customer_outstanding_report(request):

    customers = Customer.objects.all()

    data = []

    grand_total = Decimal('0')

    for customer in customers:

        debit = CustomerLedger.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('debit')
        )['total'] or Decimal('0')

        credit = CustomerLedger.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('credit')
        )['total'] or Decimal('0')

        balance = debit - credit

        if balance > 0:

            data.append({

                'customer': customer,
                'balance': balance

            })

            grand_total += balance

    return render(
        request,
        'sales/customer_outstanding_report.html',
        {
            'data': data,
            'grand_total': grand_total
        }
    )


from django.db.models import Sum
from .models import Customer, CustomerLedger


@login_required
def customer_outstanding_report(request):

    customers = Customer.objects.all()

    data = []

    for customer in customers:

        debit = CustomerLedger.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('debit')
        )['total'] or 0

        credit = CustomerLedger.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('credit')
        )['total'] or 0

        balance = debit - credit

        data.append({
            'customer': customer,
            'balance': balance
        })

    return render(
        request,
        'sales/customer_outstanding_report.html',
        {
            'data': data
        }
    )


@login_required
def sales_return_list(request):

    returns = SalesReturn.objects.select_related(
        'customer',
        'sale'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'sales/sales_return_list.html',
        {
            'returns': returns
        }
    )



@login_required
def sales_return_create(request):

    form = SalesReturnForm(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid():

            items_json = request.POST.get(
                'items_json',
                ''
            )

            if not items_json:

                return render(
                    request,
                    'sales/sales_return_create.html',
                    {
                        'form': form,
                        'error':
                        'Add at least one return item.'
                    }
                )

            items = json.loads(
                items_json
            )

            sales_return = form.save(
                commit=False
            )

            sales_return.customer = (
                sales_return.sale.customer
            )

            sales_return.created_by = (
                request.user
            )

            sales_return.save()

            total_amount = Decimal('0')

            for item in items:

                sale_item = SaleItem.objects.get(
                    id=item['sale_item']
                )

                return_qty = Decimal(
                    str(item['quantity'])
                )

                available_qty = (
                    sale_item.quantity -
                    sale_item.returned_qty
                )

                if return_qty > available_qty:

                    sales_return.delete()

                    return render(
                        request,
                        'sales/sales_return_create.html',
                        {
                            'form': form,
                            'error':
                            f'Return exceeds sold quantity '
                            f'for {sale_item.product.name}'
                        }
                    )

                amount = (
                    return_qty *
                    sale_item.rate
                )

                total_amount += amount

                SalesReturnItem.objects.create(
                    sales_return=sales_return,
                    product=sale_item.product,
                    quantity=return_qty,
                    rate=sale_item.rate,
                    amount=amount
                )

                # update returned qty

                sale_item.returned_qty += (
                    return_qty
                )

                sale_item.save()

                # increase stock

                product = sale_item.product

                product.current_stock += (
                    return_qty
                )

                product.save()

            sales_return.total_amount = (
                total_amount
            )

            sales_return.save()

            # Ledger Entry

            last_ledger = CustomerLedger.objects.filter(
                customer=sales_return.customer
            ).order_by(
                '-id'
            ).first()

            balance = (
                last_ledger.balance
                if last_ledger
                else Decimal('0')
            )

            balance -= total_amount

            CustomerLedger.objects.create(
                customer=sales_return.customer,
                entry_type='SALES_RETURN',
                debit=Decimal('0'),
                credit=total_amount,
                balance=balance,
                reference=sales_return.return_no
            )

            return redirect(
                'sales_return_list'
            )

    return render(
        request,
        'sales/sales_return_create.html',
        {
            'form': form
        }
    )


@login_required
def sale_items_json(request, sale_id):

    items = SaleItem.objects.filter(
        sale_id=sale_id
    )

    data = []

    for item in items:

        available_return = (
            item.quantity -
            item.returned_qty
        )

        data.append({
            'id': item.id,
            'product': item.product.name,
            'quantity': float(item.quantity),
            'returned_qty': float(item.returned_qty),
            'available_return': float(available_return),
            'rate': float(item.rate)
        })

    return JsonResponse(
        data,
        safe=False
    )