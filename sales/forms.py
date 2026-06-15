from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:

        model = Customer

        fields = [
            'name',
            'phone',
            'email',
            'address',
            'opening_balance',
            'is_active'
        ]

from .models import Sale


class SaleForm(forms.ModelForm):

    class Meta:

        model = Sale

        fields = [
            'customer',
            'invoice_no',
            'sale_date',
            'paid_amount'
        ]