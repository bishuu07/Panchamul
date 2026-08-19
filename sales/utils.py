from decimal import Decimal

from .models import CustomerLedger


def add_customer_ledger(
    customer,
    entry_type,
    debit=Decimal("0"),
    credit=Decimal("0"),
    bonus_quantity=Decimal("0"),
    reference=None,
    remarks=None
):

    last_entry = (
        CustomerLedger.objects
        .filter(
            customer=customer
        )
        .order_by("-id")
        .first()
    )

    previous_balance = (
        last_entry.balance
        if last_entry
        else Decimal("0")
    )

    balance = (
        previous_balance
        + debit
        - credit
    )

    entry = CustomerLedger.objects.create(
        customer=customer,
        entry_type=entry_type,
        debit=debit,
        credit=credit,
        bonus_quantity=bonus_quantity,
        balance=balance,
        reference=reference,
        remarks=remarks
    )

    return entry.balance