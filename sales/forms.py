from django import forms
from .models import Customer,CustomerPayment, SalesReturn 


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


class CustomerPaymentForm(forms.ModelForm):

    class Meta:

        model = CustomerPayment

        fields = [
            'customer',
            'payment_date',
            'amount',
            'remarks'
        ]


class SalesReturnForm(forms.ModelForm):

    class Meta:

        model = SalesReturn

        fields = [
            'return_no',
            'sale',
            'return_date',
            'remarks'
        ]

    sale = forms.ModelChoiceField(
        queryset=Sale.objects.all().order_by(
            '-id'
        )
    )