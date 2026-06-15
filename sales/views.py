from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import Customer,Sale
from .forms import CustomerForm
from decimal import Decimal
from .forms import SaleForm
import json

from inventory.models import Product

from django.contrib.auth.decorators import login_required
from .models import (
    Sale,
    SaleItem,
    CustomerLedger,
    Customer
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