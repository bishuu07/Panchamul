from django.shortcuts import render, redirect, get_object_or_404
from .models import Dealer,DealerLedger,DealerPayment,DealerReturnItem,DealerReturn
from .forms import DealerForm, DealerPaymentForm
from django.http import HttpResponse
from accounts.utils import has_permission
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import json
from inventory.models import Product,DealerStock





def dealer_list(request):

    if not has_permission(
        request.user,
        'DEALER',
        'can_view'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    dealers = Dealer.objects.all().order_by('-id')

    return render(
        request,
        'dashboard/super_admin/dealer_list.html',
        {
            'dealers': dealers
        }
    )


def dealer_create(request):

    if not has_permission(
        request.user,
        'DEALER',
        'can_add'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    form = DealerForm(
        request.POST or None
    )

    if form.is_valid():

        dealer = form.save(
            commit=False
        )

        dealer.created_by = request.user

        dealer.save()

        return redirect(
            'dealer_list'
        )

    return render(
        request,
        'dashboard/super_admin/dealer_create.html',
        {
            'form': form
        }
    )

    return render(
        request,
        'dashboard/super_admin/dealer_create.html',
        {
            'form': form
        }
    )

def dealer_edit(request, pk):

    if not has_permission(
        request.user,
        'DEALER',
        'can_edit'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    form = DealerForm(
        request.POST or None,
        instance=dealer
    )

    if form.is_valid():

        form.save()

        return redirect(
            'dealer_list'
        )

    return render(
        request,
        'dashboard/super_admin/dealer_create.html',
        {
            'form': form
        }
    )

def dealer_delete(request, pk):

    if not has_permission(
        request.user,
        'DEALER',
        'can_delete'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    dealer.is_active = False

    dealer.save()

    return redirect(
        'dealer_list'
    )

def dealer_toggle_status(request, pk):

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    dealer.is_active = not dealer.is_active

    dealer.save()

    return redirect(
        'dealer_list'
    )


from decimal import Decimal

@login_required
def dealer_payment_create(request):

    form = DealerPaymentForm(
        request.POST or None
    )

    if form.is_valid():

        payment = form.save(
            commit=False
        )

        payment.created_by = request.user

        payment.save()

        last_balance = DealerLedger.objects.filter(
            dealer=payment.dealer
        ).order_by(
            '-id'
        ).first()

        balance = (
            last_balance.balance
            if last_balance
            else Decimal('0')
        )

        balance -= payment.amount

        DealerLedger.objects.create(
            dealer=payment.dealer,
            entry_type='PAYMENT',
            debit=Decimal('0'),
            credit=payment.amount,
            balance=balance,
            reference=payment.reference_no
        )

        return redirect(
            'dealer_payment_list'
        )

    return render(
        request,
        'dashboard/dealer/dealer_payment_create.html',
        {
            'form': form
        }
    )

@login_required
def dealer_payment_list(request):

    payments = DealerPayment.objects.select_related(
        'dealer'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'dashboard/dealer/dealer_payment_list.html',
        {
            'payments': payments
        }
    )

@login_required
def dealer_ledger_list(request):

    dealers = Dealer.objects.all()

    data = []

    for dealer in dealers:

        debit = DealerLedger.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('debit')
        )['total'] or 0

        credit = DealerLedger.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('credit')
        )['total'] or 0

        balance = debit - credit

        data.append({

            'dealer': dealer,
            'debit': debit,
            'credit': credit,
            'balance': balance

        })

    return render(
        request,
        'dashboard/dealer/dealer_ledger_list.html',
        {
            'data': data
        }
    )

@login_required
def dealer_outstanding_report(request):

    dealers = Dealer.objects.all()

    data = []
    total_due = Decimal("0")

    for dealer in dealers:

        ledger = DealerLedger.objects.filter(
            dealer=dealer
        ).aggregate(
            debit=Sum("debit"),
            credit=Sum("credit")
        )

        debit = ledger["debit"] or Decimal("0")
        credit = ledger["credit"] or Decimal("0")

        balance = debit - credit

        if balance > 0:

            data.append({

                "dealer": dealer,
                "debit": debit,
                "credit": credit,
                "balance": balance,

            })

            total_due += balance

    return render(

        request,

        "dashboard/dealers/dealer_outstanding_report.html",

        {

            "data": data,
            "total_due": total_due,

        },

    )


from .models import DealerLedger


@login_required
def dealer_ledger(request, dealer_id):

    dealer = Dealer.objects.get(
        id=dealer_id
    )

    ledgers = DealerLedger.objects.filter(
        dealer=dealer
    ).order_by(
        'id'
    )

    return render(
        request,
        'dealers/dealer_ledger.html',
        {
            'dealer': dealer,
            'ledgers': ledgers
        }
    )


from django.db.models import Sum


@login_required
def dealer_outstanding_report(request):

    dealers = Dealer.objects.all()

    data = []

    for dealer in dealers:

        debit = DealerLedger.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('debit')
        )['total'] or 0

        credit = DealerLedger.objects.filter(
            dealer=dealer
        ).aggregate(
            total=Sum('credit')
        )['total'] or 0

        balance = debit - credit

        data.append({
            'dealer': dealer,
            'balance': balance
        })

    return render(
        request,
        'dashboard/dealer/dealer_outstanding_report.html',
        {
            'data': data
        }
    )


@login_required
def dealer_return_create(request):

    dealers = Dealer.objects.all()
    products = Product.objects.filter(is_active=True)

    if request.method == 'POST':

        dealer_id = request.POST.get('dealer')
        dealer = get_object_or_404(Dealer, id=dealer_id)

        items_json = request.POST.get('items_json', '')

        if not items_json:
            return render(request, 'dealers/dealer_return_create.html', {
                'dealers': dealers,
                'products': products,
                'error': 'Add at least one item.'
            })

        items = json.loads(items_json)

        # CREATE HEADER
        dealer_return = DealerReturn.objects.create(
            dealer=dealer,
            return_no=request.POST.get('return_no'),
            return_date=request.POST.get('return_date'),
            remarks=request.POST.get('remarks'),
            created_by=request.user
        )

        total_amount = Decimal('0')

        for item in items:

            product = Product.objects.get(id=item['product'])
            qty = Decimal(str(item['quantity']))
            rate = Decimal(str(item['rate']))

            # Dealer stock check
            stock = DealerStock.objects.get(dealer=dealer, product=product)

            if qty > stock.quantity:
                dealer_return.delete()
                return render(request, 'dealers/dealer_return_create.html', {
                    'dealers': dealers,
                    'products': products,
                    'error': f'Not enough dealer stock for {product.name}'
                })

            amount = qty * rate
            total_amount += amount

            # Create item
            DealerReturnItem.objects.create(
                dealer_return=dealer_return,
                product=product,
                quantity=qty,
                rate=rate,
                amount=amount
            )

            # 1. reduce dealer stock
            stock.quantity -= qty
            stock.save()

            # 2. increase company stock
            product.current_stock += qty
            product.save()

        dealer_return.total_amount = total_amount
        dealer_return.save()

        return redirect('dealer_return_list')

    return render(request, 'dealers/dealer_return_create.html', {
        'dealers': dealers,
        'products': products
    })

