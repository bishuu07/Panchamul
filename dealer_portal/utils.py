from decimal import Decimal
from .models import DealerCustomerLedger


def add_customer_ledger(
    customer,
    entry_type,
    debit=Decimal("0"),
    credit=Decimal("0")
):
    last = (
        DealerCustomerLedger.objects
        .filter(customer=customer)
        .order_by("-id")
        .first()
    )

    previous_balance = (
        last.balance if last else Decimal("0")
    )

    new_balance = (
        previous_balance +
        debit -
        credit
    )

    DealerCustomerLedger.objects.create(
        customer=customer,
        entry_type=entry_type,
        debit=debit,
        credit=credit,
        balance=new_balance
    )

    return new_balance