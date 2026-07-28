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

@login_required
def sale_create(request):

    form = SaleForm(
        request.POST or None
    )

    products = Product.objects.filter(
        is_active=True
    ).order_by(
        'name'
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
                    'sales/sale_create.html',
                    {
                        'form': form,
                        'products': products,
                        'error': 'Add at least one product.'
                    }
                )

            items = json.loads(
                items_json
            )

            total_amount = Decimal('0')

            # Stock Validation

            for item in items:

                product = Product.objects.get(
                    id=item['product']
                )

                qty = Decimal(
                    str(item['quantity'])
                )

                if qty > product.current_stock:

                    return render(
                        request,
                        'sales/sale_create.html',
                        {
                            'form': form,
                            'products': products,
                            'error':
                            f'Insufficient stock for '
                            f'{product.name}. '
                            f'Available stock: '
                            f'{product.current_stock}'
                        }
                    )

            # Create Sale

            sale = form.save(
                commit=False
            )

            sale.created_by = request.user

            sale.save()

            # Create Items

            for item in items:

                product = Product.objects.get(
                    id=item['product']
                )

                qty = Decimal(
                    str(item['quantity'])
                )

                rate = Decimal(
                    str(item['rate'])
                )

                amount = qty * rate

                total_amount += amount

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    rate=rate,
                    amount=amount
                )

                # Deduct Stock

                product.current_stock -= qty

                product.save()

            sale.total_amount = total_amount

            sale.due_amount = (
                total_amount -
                sale.paid_amount
            )

            if sale.due_amount <= 0:

                sale.status = 'PAID'

            elif sale.paid_amount > 0:

                sale.status = 'PARTIAL'

            else:

                sale.status = 'UNPAID'

            sale.save()

            # Customer Ledger

            last_balance = CustomerLedger.objects.filter(
                customer=sale.customer
            ).order_by(
                '-id'
            ).first()

            balance = (
                last_balance.balance
                if last_balance
                else Decimal('0')
            )

            balance += total_amount

            CustomerLedger.objects.create(
                customer=sale.customer,
                entry_type='SALE',
                debit=total_amount,
                credit=Decimal('0'),
                balance=balance,
                reference=sale.invoice_no
            )

            if sale.paid_amount > 0:

                balance -= sale.paid_amount

                CustomerLedger.objects.create(
                    customer=sale.customer,
                    entry_type='PAYMENT',
                    debit=Decimal('0'),
                    credit=sale.paid_amount,
                    balance=balance,
                    reference=sale.invoice_no
                )

            return redirect(
                'sale_list'
            )

    return render(
        request,
        'sales/sale_create.html',
        {
            'form': form,
            'products': products
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

    customer = Customer.objects.get(
        id=customer_id
    )

    ledgers = CustomerLedger.objects.filter(
        customer=customer
    ).order_by(
        'id'
    )

    return render(
        request,
        'sales/customer_ledger_detail.html',
        {
            'customer': customer,
            'ledgers': ledgers
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